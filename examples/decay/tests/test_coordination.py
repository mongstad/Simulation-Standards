# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Output coordination regressions; all directories are disposable."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import simulate


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if k not in ('SIMSHELF_OUTPUT_DIR', 'SIMSHELF_OUTPUT_POLICY')}

    def command(self, *extra):
        return [sys.executable, '-B', str(ROOT/'simulate.py'), '-k', '1e-1', '-n', '0010', '--label', '', *extra]

    def launch(self, output=None, extra=(), policy="per_run"):
        env = dict(self.env)
        if output is not None:
            env['SIMSHELF_OUTPUT_DIR'] = str(output)
            env['SIMSHELF_OUTPUT_POLICY'] = policy
        return subprocess.run(self.command(*extra), env=env, cwd=self.base,
                              capture_output=True, text=True, timeout=10)

    def assert_direct(self, root, result, series=True):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(p.is_dir() for p in root.iterdir()))
        names = {p.name for p in root.iterdir()}
        self.assertTrue({'summary.json', 'provenance.json', '.swss-run'} <= names)
        self.assertEqual('measurements.csv' in names, series)
        provenance = json.loads((root/'provenance.json').read_text())
        summary = json.loads((root/'summary.json').read_text())
        self.assertEqual(provenance['output_directory'], str(root))
        self.assertEqual(provenance['output_allocation'], 'per_run')
        self.assertEqual(provenance['argv'], self.command()[3:] + ([] if series else ['--no-series']))
        self.assertEqual(provenance['simulation_version'], '0.1.2')
        self.assertEqual(summary['status'], 'completed')
        self.assertEqual(summary['output_directory'], str(root))
        self.assertEqual(summary['output_allocation'], 'per_run')
        self.assertEqual(summary['run_id'], provenance['run_id'])
        self.assertEqual((root/'.swss-run').read_text().strip(), summary['run_id'])
        log, = root.glob('*.log')
        self.assertIn('output_directory=' + str(root), log.read_text())
        self.assertIn('status=completed exit_code=0', log.read_text())

    def test_preallocated_root_and_optional_series(self):
        for series in (True, False):
            root = self.base/str(series)
            root.mkdir()
            self.assert_direct(root, self.launch(root, () if series else ('--no-series',)), series)
        self.assertFalse((self.base/'outputs').exists())

    def test_standalone_and_coordinated_scientific_results_identical(self):
        for method in ('euler', 'exact'):
            standalone = self.launch(extra=('--method', method))
            self.assertEqual(standalone.returncode, 0, standalone.stderr)
            roots = list((self.base/'outputs').iterdir())
            standalone_root = next(p for p in roots if method == 'euler' or p != first)
            if method == 'euler':
                first = standalone_root
            root = self.base/method
            root.mkdir()
            result = self.launch(root, ('--method', method))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root/'measurements.csv').read_bytes(), (standalone_root/'measurements.csv').read_bytes())
            self.assertEqual(json.loads((root/'summary.json').read_text())['last_sample'],
                             json.loads((standalone_root/'summary.json').read_text())['last_sample'])
        self.assertEqual(len(list((self.base/'outputs').iterdir())), 2)

    def test_invalid_paths_no_replacement(self):
        file = self.base/'file'
        file.write_text('preserve')
        link = self.base/'link'
        link.symlink_to(self.base, target_is_directory=True)
        for supplied in ('', 'relative', self.base/'missing', file, link):
            with self.subTest(path=str(supplied)):
                before = set(self.base.iterdir())
                result = self.launch(supplied)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('SIMSHELF_OUTPUT_DIR', result.stderr)
                self.assertEqual(before, set(self.base.iterdir()))
        self.assertEqual(file.read_text(), 'preserve')

    def test_inaccessible_directory(self):
        root = self.base/'denied'
        root.mkdir()
        # Deterministic permission failure, including privileged test environments.
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(root), 'SIMSHELF_OUTPUT_POLICY': 'per_run'}), \
             patch.object(simulate.os, 'access', return_value=False), \
             contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(simulate.main(['--rate', '1']), 1)
        self.assertIn('readable, writable and searchable', error.getvalue())
        self.assertEqual(list(root.iterdir()), [])
        if os.geteuid() != 0:
            root.chmod(0)
            try:
                result = self.launch(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('SIMSHELF_OUTPUT_DIR', result.stderr)
            finally:
                root.chmod(0o700)
            self.assertEqual(list(root.iterdir()), [])

    def test_explicit_output_parent_conflicts(self):
        root = self.base/'allocated'
        root.mkdir()
        for args in (('--output-parent', 'outputs'), ('--output-parent=outputs',),
                     ('--output-parent', str(root))):
            result = self.launch(root, args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('explicit --output-parent conflicts', result.stderr)
            self.assertEqual(list(root.iterdir()), [])
        self.assert_direct(root, self.launch(root))  # Default is not explicit.

    def test_existing_files_preserved(self):
        for name in ('summary.json', 'provenance.json', 'measurements.csv', 'prior.log', '.swss-run'):
            root = self.base/name
            root.mkdir()
            (root/name).write_bytes(b'historical evidence')
            result = self.launch(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, {name: b'historical evidence'})

    def test_concurrent_distinct_and_shared_roots(self):
        for shared in (False, True):
            roots = [self.base/f'{shared}-{i}' for i in range(2)]
            for root in roots:
                root.mkdir()
            targets = [roots[0], roots[0]] if shared else roots
            processes = [subprocess.Popen(self.command(), env={**self.env, 'SIMSHELF_OUTPUT_DIR': str(root), 'SIMSHELF_OUTPUT_POLICY': 'per_run'},
                                          cwd=self.base, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                         for root in targets]
            for process in processes:
                process.communicate(timeout=10)
            self.assertEqual(sorted(p.returncode for p in processes), [0, 1] if shared else [0, 0])
            for root in set(targets):
                self.assertEqual(json.loads((root/'summary.json').read_text())['status'], 'completed')
                self.assertFalse(any(p.is_dir() for p in root.iterdir()))
                before = {p.name: p.read_bytes() for p in root.iterdir()}
                self.assertNotEqual(self.launch(root).returncode, 0)
                self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_coordinated_failure_preserves_claim_and_partial_evidence(self):
        root = self.base/'failed'
        root.mkdir()
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(root), 'SIMSHELF_OUTPUT_POLICY': 'per_run'}), \
             patch.object(simulate, 'advance', side_effect=ArithmeticError('injected')), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(simulate.main(['--rate', '1']), 1)
        self.assertEqual(json.loads((root/'summary.json').read_text())['status'], 'failed')
        before = {p.name: p.read_bytes() for p in root.iterdir()}
        self.assertNotEqual(self.launch(root).returncode, 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_fixed_consecutive_runs_preserve_occupied_parent(self):
        parent = self.base/'new'/'shared'
        roots = []
        for _ in range(2):
            before = set(parent.iterdir()) if parent.exists() else set()
            result = self.launch(parent, policy='fixed')
            self.assertEqual(result.returncode, 0, result.stderr)
            child, = set(parent.iterdir()) - before
            self.assertTrue(child.name.startswith('run_'))
            self.assertFalse(any(p.is_dir() for p in child.iterdir()))
            provenance = json.loads((child/'provenance.json').read_text())
            summary = json.loads((child/'summary.json').read_text())
            self.assertEqual(provenance['output_allocation'], 'fixed')
            self.assertEqual(provenance['output_directory'], str(child))
            self.assertEqual(summary['output_directory'], str(child))
            self.assertEqual(summary['output_allocation'], 'fixed')
            self.assertEqual(provenance['argv'], self.command()[3:])
            self.assertEqual(provenance['resolved']['steps'], 10)
            self.assertIn('allocation=fixed', next(child.glob('*.log')).read_text())
            roots.append(child)
            if len(roots) == 1:
                saved = {p: p.read_bytes() for p in child.iterdir()}
                (parent/'historical.txt').write_text('keep')
        self.assertNotEqual(*roots)
        self.assertTrue(all(p.read_bytes() == data for p,data in saved.items()))
        self.assertEqual((parent/'historical.txt').read_text(), 'keep')
        self.assertEqual((roots[0]/'measurements.csv').read_bytes(), (roots[1]/'measurements.csv').read_bytes())

    def test_fixed_concurrent_runs_allocate_distinct_children(self):
        parent = self.base/'shared'
        processes = [subprocess.Popen(self.command(), cwd=self.base,
                     env={**self.env, 'SIMSHELF_OUTPUT_DIR': str(parent), 'SIMSHELF_OUTPUT_POLICY': 'fixed'},
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for process in processes:
            _, error = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, error)
        children = list(parent.iterdir())
        self.assertEqual(len(children), 2)
        self.assertEqual((children[0]/'measurements.csv').read_bytes(), (children[1]/'measurements.csv').read_bytes())
        self.assertFalse(any(p.is_dir() for child in children for p in child.iterdir()))

    def test_adapter_configuration_is_explicit(self):
        parent = self.base/'unchanged'
        parent.mkdir()
        cases = [{'SIMSHELF_OUTPUT_DIR': str(parent)},
                 {'SIMSHELF_OUTPUT_POLICY': 'fixed'}, {'SIMSHELF_OUTPUT_POLICY': 'per_run'},
                 {'SIMSHELF_OUTPUT_POLICY': ''}]
        cases += [{'SIMSHELF_OUTPUT_DIR': str(parent), 'SIMSHELF_OUTPUT_POLICY': policy}
                  for policy in ('', 'unknown', 'FIXED', ' per_run')]
        for extra in cases:
            with self.subTest(extra=extra):
                result = subprocess.run(self.command(), cwd=self.base, env={**self.env, **extra},
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertIn('requires SIMSHELF_OUTPUT_DIR', result.stderr)
                self.assertEqual(list(parent.iterdir()), [])
        self.assertFalse((self.base/'outputs').exists())

    def test_fixed_invalid_paths_and_conflicts(self):
        file = self.base/'file'
        file.write_text('unchanged')
        real = self.base/'real'
        real.mkdir()
        link = self.base/'link'
        link.symlink_to(real, target_is_directory=True)
        for target in ('', 'relative', file, link, link/'child'):
            result = self.launch(target, policy='fixed')
            self.assertEqual(result.returncode, 1)
            self.assertIn('SIMSHELF_OUTPUT_DIR', result.stderr)
        self.assertEqual(file.read_text(), 'unchanged')
        self.assertEqual(list(real.iterdir()), [])
        for extra in (('--output-parent', str(real)), ('--output-parent=outputs',)):
            result = self.launch(real, extra, policy='fixed')
            self.assertEqual(result.returncode, 1)
            self.assertIn('explicit --output-parent conflicts', result.stderr)
            self.assertEqual(list(real.iterdir()), [])
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(real), 'SIMSHELF_OUTPUT_POLICY': 'fixed'}), \
             patch.object(simulate.os, 'access', return_value=False), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(simulate.main(['--rate','1']), 1)
        self.assertEqual(list(real.iterdir()), [])

    def test_fixed_child_collision_preserves_evidence(self):
        parent = self.base/'fixed'
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(parent), 'SIMSHELF_OUTPUT_POLICY': 'fixed'}):
            root, mode = simulate.output_directory({}, [], 'fixed-stamp', 'fixed-id')
            (root/'summary.json').write_text('preserve')
            with self.assertRaises(FileExistsError):
                simulate.output_directory({}, [], 'fixed-stamp', 'fixed-id')
            self.assertEqual((root/'summary.json').read_text(), 'preserve')
            self.assertEqual(list(parent.iterdir()), [root])

    def test_all_modes_preserve_scientific_values(self):
        for method in ('euler', 'exact'):
            standalone_parent = self.base/(method+'-standalone')
            result = self.launch(extra=('--method',method,'--output-parent',str(standalone_parent)))
            self.assertEqual(result.returncode,0,result.stderr)
            standalone, = standalone_parent.iterdir()
            fixed_parent = self.base/(method+'-fixed')
            result = self.launch(fixed_parent, ('--method',method), policy='fixed')
            self.assertEqual(result.returncode,0,result.stderr)
            fixed, = fixed_parent.iterdir()
            allocated = self.base/(method+'-allocated')
            allocated.mkdir()
            self.assertEqual(self.launch(allocated, ('--method',method)).returncode,0)
            for root in (fixed, allocated):
                self.assertEqual((root/'measurements.csv').read_bytes(),(standalone/'measurements.csv').read_bytes())
                self.assertEqual(json.loads((root/'summary.json').read_text())['last_sample'],
                                 json.loads((standalone/'summary.json').read_text())['last_sample'])

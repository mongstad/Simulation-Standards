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
        self.env = {k: v for k, v in os.environ.items() if k != 'SIMSHELF_OUTPUT_DIR'}

    def command(self, *extra):
        return [sys.executable, '-B', str(ROOT/'simulate.py'), '-k', '1e-1', '-n', '0010', '--label', '', *extra]

    def launch(self, output=None, extra=()):
        env = dict(self.env)
        if output is not None:
            env['SIMSHELF_OUTPUT_DIR'] = str(output)
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
        self.assertEqual(provenance['output_allocation'], 'coordinated')
        self.assertEqual(provenance['argv'], self.command()[3:] + ([] if series else ['--no-series']))
        self.assertEqual(provenance['simulation_version'], '0.1.1')
        self.assertEqual(summary['status'], 'completed')
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
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(root)}), \
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
            processes = [subprocess.Popen(self.command(), env={**self.env, 'SIMSHELF_OUTPUT_DIR': str(root)},
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
        with patch.dict(os.environ, {'SIMSHELF_OUTPUT_DIR': str(root)}), \
             patch.object(simulate, 'advance', side_effect=ArithmeticError('injected')), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(simulate.main(['--rate', '1']), 1)
        self.assertEqual(json.loads((root/'summary.json').read_text())['status'], 'failed')
        before = {p.name: p.read_bytes() for p in root.iterdir()}
        self.assertNotEqual(self.launch(root).returncode, 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

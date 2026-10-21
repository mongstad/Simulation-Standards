# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check_contract
import simulate


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'simulate.py').read_bytes()
        self.metadata = (ROOT / 'swss.toml').read_bytes()
        self.rows = tomllib.loads(self.metadata.decode())['swss']['parameters']

    def test_static_and_actual_parser_agreement(self):
        self.assertEqual(check_contract.compare(self.source, self.metadata), 12)
        actions = [a for a in simulate.build_parser()._actions if not isinstance(a, argparse._HelpAction)]
        self.assertEqual(len(actions), len(self.rows))
        types = {'integer': int, 'float': float, 'string': str}
        for row, action in zip(self.rows, actions):
            self.assertEqual(row['options'], action.option_strings)
            self.assertEqual(row['required'], action.required)
            self.assertEqual(row['kind'], 'option')
            self.assertEqual(row['choices'] if 'choices' in row else None, action.choices)
            self.assertEqual(row.get('default'), action.default)
            if row['action'] == 'store':
                self.assertIs(type(action), argparse._StoreAction)
                self.assertIs(action.type, types[row['type']])
            else:
                self.assertEqual(row['type'], 'boolean')
                self.assertIs(type(action), {'store_true': argparse._StoreTrueAction,
                                            'store_false': argparse._StoreFalseAction}[row['action']])
            self.assertLessEqual(len(row['help'].encode()), 256)

    def test_isolated_negative_metadata_fixtures(self):
        cases = json.loads((ROOT / 'tests/fixtures/mismatches.json').read_text())
        for case in cases:
            with self.subTest(case=case['name']):
                self.assertIn(case['old'], self.metadata.decode())
                changed = self.metadata.decode().replace(case['old'], case['new'], 1).encode()
                with self.assertRaises(ValueError):
                    check_contract.compare(self.source, changed)
        with self.assertRaisesRegex(ValueError, 'stale source binding'):
            check_contract.compare(self.source + b'\n# source changed\n', self.metadata)

    def test_static_check_does_not_execute_source_or_write(self):
        hostile = self.source + b'\nraise RuntimeError("must never execute")\n'
        metadata = self.metadata.replace(hashlib.sha256(self.source).hexdigest().encode(),
                                         hashlib.sha256(hostile).hexdigest().encode())
        with patch('builtins.exec', side_effect=AssertionError('execution')), \
             patch('builtins.open', side_effect=AssertionError('file access')), \
             patch('subprocess.Popen', side_effect=AssertionError('subprocess')), \
             patch('socket.socket', side_effect=AssertionError('network')):
            self.assertEqual(check_contract.compare(hostile, metadata), 12)

    def test_parser_semantics(self):
        p = simulate.build_parser()
        a = p.parse_args(['-k', '1e-1', '-n', '0010', '--rate-scale', '0.5', '--method', 'exact', '--label', '', '--progress', '--no-series'])
        self.assertEqual((a.rate, a.steps, a.rate_scale, a.label, a.progress, a.series), (.1, 10, .5, '', True, False))
        self.assertIsNone(a.dt)
        resolved = simulate.resolve(a)
        self.assertEqual(resolved['dt'], 1.0)
        self.assertEqual(p.parse_args(['--rate', '1']).progress, False)
        self.assertEqual(p.parse_args(['--rate', '1']).series, True)
        for argv in ([], ['--rate'], ['--rate', 'wrong'], ['--rate', '1', '--steps', '11'],
                     ['--rate', '1', '--rate-scale', '3'], ['--rate', '1', '--method', 'bad']):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                p.parse_args(argv)
            self.assertEqual(error.exception.code, 2)
        for value in ('nan', 'inf', '-1', '0'):
            with self.assertRaises(ValueError):
                simulate.resolve(p.parse_args(['--rate', value]))


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)

    def command(self, argv):
        return [sys.executable, '-B', str(ROOT / 'simulate.py'), *argv, '--output-parent', str(self.parent)]

    def launch(self, argv):
        before = set(self.parent.iterdir())
        result = subprocess.run(self.command(argv), text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        root, = set(self.parent.iterdir()) - before
        return root, result

    def test_numeric_reference_exact_argv_and_provenance(self):
        argv = ['-k', '1e-1', '-n', '0010', '--dt=0.25', '--label', '', '--method', 'euler']
        root, _ = self.launch(argv)
        provenance = json.loads((root / 'provenance.json').read_text())
        self.assertEqual(provenance['argv'], self.command(argv)[3:])
        self.assertEqual(provenance['resolved']['steps'], 10)
        self.assertEqual(provenance['resolved']['dt'], .25)
        self.assertEqual(provenance['source_sha256']['simulate.py'], hashlib.sha256((ROOT/'simulate.py').read_bytes()).hexdigest())
        with (root / 'measurements.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 11)
        for i, row in enumerate(rows):
            expected = (1 - .1 * .25) ** i
            self.assertAlmostEqual(float(row['concentration']), expected, places=14)
            self.assertEqual(float(row['time']), i * .25)
            analytic = math.exp(-.1 * i * .25)
            self.assertAlmostEqual(float(row['analytic_concentration']), analytic, places=14)
            self.assertAlmostEqual(float(row['absolute_error']), abs(expected - analytic), places=14)
        summary = json.loads((root / 'summary.json').read_text())
        self.assertEqual(summary['status'], 'completed')
        self.assertEqual(summary['output_directory'], str(root))
        self.assertEqual(summary['run_id'], provenance['run_id'])
        self.assertFalse(summary['verified'])
        log, = root.glob('*.log')
        self.assertIn(provenance['run_id'], log.name)
        self.assertIn('status=completed exit_code=0', log.read_text())

    def test_instrumentation_independence_and_exact_solution(self):
        base = ['--rate', '.5', '--initial', '2', '--method', 'exact']
        first, _ = self.launch(base)
        saved = {p.name: p.read_bytes() for p in first.iterdir()}
        second, result = self.launch(base + ['--no-series', '--progress', '--sample-every', '5'])
        one = json.loads((first/'summary.json').read_text())['last_sample']
        two = json.loads((second/'summary.json').read_text())['last_sample']
        self.assertEqual(one, two)
        self.assertAlmostEqual(one['concentration'], 2 * math.exp(-.5), places=14)
        self.assertFalse((second/'measurements.csv').exists())
        telemetry = [json.loads(s) for s in result.stdout.splitlines() if s.startswith('{')]
        self.assertEqual([r['current'] for r in telemetry], [0, 5, 10, 15, 20])
        self.assertTrue(all(r['total'] == 20 for r in telemetry))
        self.assertEqual(telemetry[-1]['concentration'], one['concentration'])
        self.assertEqual(saved, {p.name: p.read_bytes() for p in first.iterdir()})

    def test_simultaneous_runs_and_deterministic_series(self):
        processes = [subprocess.Popen(self.command(['--rate', '1']), stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for process in processes:
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, err)
        roots = list(self.parent.iterdir())
        self.assertEqual(len(roots), 2)
        self.assertEqual((roots[0]/'measurements.csv').read_bytes(), (roots[1]/'measurements.csv').read_bytes())

    def test_default_and_custom_parents_preserve_science_and_evidence(self):
        for method in ('euler', 'exact'):
            argv = ['-k', '1e-1', '-n', '0010', '--label', '', '--method', method]
            saved = {}
            measurements = None
            final = None
            for extra, parent in (([], self.parent/'outputs'),
                                  (['--output-parent', 'nested/custom'], self.parent/'nested/custom'),
                                  (['--output-parent=nested/custom'], self.parent/'nested/custom')):
                before = set(parent.iterdir()) if parent.exists() else set()
                result = subprocess.run([sys.executable, '-B', str(ROOT/'simulate.py'), *argv, *extra],
                                        cwd=self.parent, text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                root, = set(parent.iterdir()) - before
                self.assertTrue(root.name.startswith('run_'))
                self.assertFalse(any(p.is_dir() for p in root.iterdir()))
                log, = root.glob('*.log')
                self.assertEqual({p.name for p in root.iterdir()},
                                 {'provenance.json', 'summary.json', 'measurements.csv', log.name})
                provenance = json.loads((root/'provenance.json').read_text())
                summary = json.loads((root/'summary.json').read_text())
                self.assertEqual(provenance['argv'], argv + extra)
                self.assertEqual(provenance['output_directory'], str(root))
                self.assertEqual(summary['output_directory'], str(root))
                self.assertEqual(provenance['simulation_version'], simulate.VERSION)
                self.assertEqual(summary['status'], 'completed')
                self.assertIn('output_directory=' + str(root), log.read_text())
                data = (root/'measurements.csv').read_bytes()
                if measurements is not None:
                    self.assertEqual(data, measurements)
                    self.assertEqual(summary['last_sample'], final)
                measurements, final = data, summary['last_sample']
                self.assertTrue(all(p.read_bytes() == content for p, content in saved.items()))
                saved.update({p: p.read_bytes() for p in root.iterdir()})

    def test_parent_file_and_allocation_failure_preserve_evidence(self):
        occupied = self.parent/'occupied'
        occupied.write_bytes(b'previous evidence')
        for parent in (occupied, occupied/'child'):
            with contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(simulate.main(['--rate', '1', '--output-parent', str(parent)]), 1)
            self.assertIn('run/evidence failure:', error.getvalue())
            self.assertEqual(occupied.read_bytes(), b'previous evidence')
        with patch.object(simulate.Path, 'mkdir', side_effect=PermissionError('allocation denied')), \
             contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(simulate.main(['--rate', '1', '--output-parent', str(self.parent)]), 1)
        self.assertIn('allocation denied', error.getvalue())
        self.assertEqual(list(self.parent.iterdir()), [occupied])

    def test_exclusive_root_collision(self):
        args = ['--rate', '1', '--output-parent', str(self.parent)]
        with patch.object(simulate, 'datetime') as clock, patch.object(simulate.uuid, 'uuid4') as uuid:
            from datetime import datetime, timezone
            clock.now.return_value = datetime(2026, 1, 1, tzinfo=timezone.utc)
            uuid.return_value.hex = 'fixed-collision-test'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(simulate.main(args), 0)
            root, = self.parent.iterdir()
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(simulate.main(args), 1)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_failure_and_handled_interruption(self):
        for failure, status, code in [(ArithmeticError('injected failure'), 'failed', 1), (KeyboardInterrupt(), 'cancelled', 130)]:
            before = set(self.parent.iterdir())
            with patch.object(simulate, 'advance', side_effect=failure), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(simulate.main(['--rate', '1', '--output-parent', str(self.parent)]), code)
            root, = set(self.parent.iterdir()) - before
            self.assertEqual(json.loads((root/'summary.json').read_text())['status'], status)
            self.assertIn('status=' + status, next(root.glob('*.log')).read_text())
            with (root/'measurements.csv').open() as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 1)
            saved = {p: p.read_bytes() for p in root.iterdir()}
            retry, _ = self.launch(['--rate', '1'])
            self.assertNotEqual(root, retry)
            self.assertTrue(all(p.read_bytes() == content for p, content in saved.items()))

    def test_evidence_io_failure_nonzero(self):
        original = simulate.write_json
        def fail_summary(path, value):
            if path.name == 'summary.json':
                raise OSError('injected storage failure')
            return original(path, value)
        with patch.object(simulate, 'write_json', side_effect=fail_summary), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(simulate.main(['--rate', '1', '--output-parent', str(self.parent)]), 1)
        root, = self.parent.iterdir()
        self.assertFalse((root/'summary.json').exists())
        self.assertNotIn('status=completed', next(root.glob('*.log')).read_text())

    def test_sigterm_records_cancellation(self):
        # Inject a real signal at a deterministic solver boundary in a child process.
        code = """import os, signal, sys
sys.path.insert(0, sys.argv[1])
import simulate
def stop(*args):
    os.kill(os.getpid(), signal.SIGTERM)
simulate.advance = stop
raise SystemExit(simulate.main(['--rate', '1', '--output-parent', sys.argv[2]]))
"""
        result = subprocess.run([sys.executable, '-B', '-c', code, str(ROOT), str(self.parent)],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 130, result.stderr)
        root, = self.parent.iterdir()
        self.assertEqual(json.loads((root/'summary.json').read_text())['status'], 'cancelled')

    def test_invalid_cli_never_allocates_run(self):
        for argv in ([], ['--rate', 'nan'], ['--rate', '1', '--dt', '2']):
            result = subprocess.run(self.command(argv), capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 2)
        self.assertEqual(list(self.parent.iterdir()), [])


if __name__ == '__main__':
    unittest.main()

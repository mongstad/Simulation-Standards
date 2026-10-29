# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Executable observations keyed to all 41 SWSS output-location cases."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import output_contract as contract

MINIMAL = b'[swss]\nschema_version = 3\nentrypoint = "simulate.py"\nsimulation_version = "0.1.4"\n'
BINDING = b'''output_parent_parameter = "destination"
[[swss.parameters]]
id = "destination"
kind = "option"
options = ["--output-parent", "-o"]
required = false
type = "string"
action = "store"
help = "Parent"
default = "outputs"
'''


class OutputCases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'
        shutil.copytree(ROOT, self.project, ignore=shutil.ignore_patterns('__pycache__'))
        self.other = self.base / 'other'
        self.other.mkdir()
        self.external = self.base / 'external'
        self.source = self.project / 'solver/helper.py'
        self.source.parent.mkdir()
        self.source.write_text('legitimate source')
        self.inputs = self.project / 'inputs/initial.json'
        self.inputs.parent.mkdir()
        self.inputs.write_text('legitimate input')
        self.notes = self.project / 'outputs_notes/analysis.py'
        self.notes.parent.mkdir()
        self.notes.write_text('legitimate lookalike')
        self.protected = [self.project / n for n in ('simulate.py', 'swss.toml', 'solver', 'inputs', 'outputs_notes')]
        self.old = self.project / 'outputs/run_old/model.py'
        self.old.parent.mkdir(parents=True)
        self.old.write_bytes(b'old generated evidence')

    def discover(self, metadata=MINIMAL, argv=(), **kwargs):
        return contract.resolve_parent(metadata, list(argv), self.project, 'simulate.py', **kwargs)

    def snap(self, *extra):
        return contract.snapshot(self.project, [self.project / 'outputs', *extra], self.protected)

    def launch(self, argv=(), *, nested=False, root=True):
        if nested:
            solver = self.project / 'solver'
            for name in ('simulate.py', 'output_contract.py'):
                shutil.copyfile(self.project / name, solver / name)
            program = "import sys; sys.path.insert(0, sys.argv[1]); import simulate; raise SystemExit(simulate.main(sys.argv[3:], simulation_root=sys.argv[2]))"
            cmd = [sys.executable, '-B', '-c', program, str(solver), str(self.project) if root else '']
        else:
            cmd = [sys.executable, '-B', str(self.project / 'simulate.py')]
        result = subprocess.run([*cmd, '--rate', '1', *argv], cwd=self.other, capture_output=True, text=True, timeout=10)
        return result

    def run_root(self, argv=(), **kwargs):
        result = self.launch(argv, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(result.stdout.strip().split('run_directory=')[-1])

    def test_S1_nested_foreign_cwd(self):
        run = self.run_root(nested=True)
        self.assertEqual(run.parent, self.project / 'outputs')
        provenance = json.loads((run / 'provenance.json').read_text())
        self.assertEqual(provenance['selected_entrypoint'], 'solver/simulate.py')
        self.assertIn('solver/simulate.py', provenance['source_sha256'])
        self.assertFalse((self.other / 'outputs').exists())
        self.assertFalse((self.project / 'solver/outputs').exists())

    def test_S2_successive_snapshots(self):
        before = self.snap()
        first, second = self.run_root(), self.run_root()
        self.assertNotEqual(first, second)
        self.assertEqual(before, self.snap())
        self.assertEqual(self.old.read_bytes(), b'old generated evidence')

    def test_S3_concurrent(self):
        cmd = [sys.executable, '-B', str(self.project / 'simulate.py'), '--rate', '1']
        jobs = [subprocess.Popen(cmd, cwd=self.other, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        roots = []
        for job in jobs:
            out, err = job.communicate(timeout=10)
            self.assertEqual(job.returncode, 0, err)
            roots.append(Path(out.decode().strip().split('run_directory=')[-1]))
        self.assertNotEqual(*roots)
        self.assertEqual(*(r.joinpath('measurements.csv').read_bytes() for r in roots))

    def test_S4_collision(self):
        sys.path.insert(0, str(ROOT))
        import simulate
        config = {'output_parent': str(self.external), 'simulation_root': str(self.project)}
        run = simulate.output_directory(config, '20261029T120000Z', 'fixed')
        (run / 'sentinel').write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):
            simulate.output_directory(config, '20261029T120000Z', 'fixed')
        self.assertEqual((run / 'sentinel').read_bytes(), b'preserve')

    def test_S5_internal_parent(self):
        parent = self.project / 'results/nested'
        old = parent / 'run_old/model.py'
        old.parent.mkdir(parents=True)
        old.write_bytes(b'old')
        before = self.snap(parent)
        self.assertEqual(self.run_root(['--output-parent', 'results/nested']).parent, parent)
        self.assertEqual(before, self.snap(parent))
        self.assertEqual(old.read_bytes(), b'old')

    def test_S6_external_parent(self):
        before = self.snap()
        first = self.run_root(['-o', str(self.external)])
        saved = {p.name: p.read_bytes() for p in first.iterdir()}
        second = self.run_root(['-o', str(self.external)])
        self.assertNotEqual(first, second)
        self.assertEqual(saved, {p.name: p.read_bytes() for p in first.iterdir()})
        self.assertEqual(before, self.snap(self.external))

    def test_S7_retained_source(self):
        before = self.snap()
        for p in (self.source, self.inputs, self.notes):
            data = p.read_bytes()
            p.write_bytes(data + b'changed')
            self.assertNotEqual(before, self.snap())
            p.write_bytes(data)
        self.assertIn('swss.toml', before)
        self.assertNotIn('outputs/run_old/model.py', before)

    def test_S8_root_entrypoint(self):
        self.assertEqual(self.run_root().parent, self.project / 'outputs')

    def test_S9_no_companion_and_ambiguous_root(self):
        (self.project / 'swss.toml').unlink()
        self.assertEqual(self.run_root(nested=True).parent, self.project / 'outputs')
        self.assertNotEqual(self.launch(nested=True, root=False).returncode, 0)

    def test_S10_science_and_argv(self):
        previous = None
        for extra in ([], ['-o', 'results'], ['--output-parent=' + str(self.external)]):
            argv = ['-n', '0010', '--label=', '--method', 'exact', *extra]
            root = self.run_root(argv)
            data = (root / 'measurements.csv').read_bytes()
            if previous is not None:
                self.assertEqual(previous, data)
            previous = data
            self.assertEqual(json.loads((root / 'provenance.json').read_text())['argv'], ['--rate', '1', *argv])

    @unittest.skip('C1: no coordinated-root adapter or recorder implemented')
    def test_C1_direct_root(self): pass
    @unittest.skip('C2: no coordinated allocation ownership/overlap protocol implemented')
    def test_C2_concurrent_agreement(self): pass
    @unittest.skip('C3: no coordinated destination argument contract implemented')
    def test_C3_conflict(self): pass

    def test_C4_standalone_only(self):
        self.run_root()
        before = set((self.project / 'outputs').iterdir())
        self.assertNotEqual(self.launch(['--coordinated-root', str(self.external)]).returncode, 0)
        self.assertEqual(before, set((self.project / 'outputs').iterdir()))
        self.assertFalse(self.external.exists())

    @unittest.skip('C5: no coordinated claim/reuse mechanism; standalone failures tested separately')
    def test_C5_occupied_coordinated_root(self): pass
    @unittest.skip('C6: no recorder/budget implementation')
    def test_C6_capture_limits(self): pass

    def test_N1_unsafe_parent(self):
        occupied = self.base / 'occupied'
        occupied.write_bytes(b'keep')
        for value in ('', '../escape', 'https://example.invalid/path', str(occupied), str(occupied / 'child')):
            with self.subTest(value=value):
                self.assertNotEqual(self.launch(['--output-parent', value]).returncode, 0)
        self.assertEqual(occupied.read_bytes(), b'keep')

    @unittest.skip('N1b: actual mount availability/identity requires platform-specific volume contract')
    def test_N1b_missing_mount(self): pass

    def test_N2_overlap(self):
        for parent in (self.project, self.base, self.project / 'solver', self.project / 'inputs'):
            with self.subTest(parent=parent), self.assertRaises(ValueError):
                self.snap(parent)
            self.assertNotEqual(self.launch(['-o', str(parent)]).returncode, 0)

    def test_N3_alias(self):
        link = self.project / 'alias'
        link.symlink_to(self.other, target_is_directory=True)
        self.assertNotEqual(self.launch(['-o', str(link / 'new')]).returncode, 0)
        with self.assertRaises(ValueError): self.snap()
        self.assertEqual(list(self.other.iterdir()), [])

    def test_N4_identity_substitution(self):
        p = self.project / 'replace'
        p.mkdir()
        guards = contract.identities(p)
        p.rename(self.project / 'old_replace')
        p.mkdir()
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            contract.recheck(guards)

    def test_N5_literal_syntax(self):
        for value in ('$NAME', '~literal', 'literal*'):
            self.assertEqual(self.run_root(['-o', value]).parent, self.project / value)

    def test_N6_legacy_extensions(self):
        legacy = MINIMAL.replace(b'= 3', b'= 2')
        self.assertEqual(contract.parse(legacy + b'[extensions.note]\ntext="anything"\n')[0]['schema_version'], 2)
        for field in (b'output_parent="outputs"\n', b'output_parent_parameter="destination"\n'):
            with self.assertRaises(ValueError): contract.parse(legacy + field)

    def test_N7_stale_unassociated(self):
        for metadata in (MINIMAL.replace(b'simulate.py', b'other.py'), b'', MINIMAL.replace(b'= 3', b'= 4')):
            with self.assertRaises(ValueError): self.discover(metadata)
        manifest = MINIMAL + b'[[swss.source_files]]\npath="simulate.py"\nsha256="' + b'0'*64 + b'"\n'
        with self.assertRaises(ValueError): self.discover(manifest, sources={'simulate.py': b'changed'})

    def test_N8_legacy_execution(self):
        legacy = ROOT.parent / 'decay-v2'
        result = subprocess.run([sys.executable, '-B', str(legacy / 'simulate.py'), '--rate', '1'], cwd=self.other, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        root, = (self.other / 'outputs').iterdir()
        self.assertEqual(json.loads((root / 'provenance.json').read_text())['swss_version'], '2.0')

    def test_N9_historical_preservation(self):
        archive = self.base / 'history.json'
        archive.write_text(json.dumps({'old_snapshot': {'outputs/run_old/model.py': 'historical'}, 'argv': ['0010']}))
        before = archive.read_bytes()
        self.run_root()
        self.snap()
        self.assertEqual(before, archive.read_bytes())
        self.assertEqual(self.old.read_bytes(), b'old generated evidence')

    def test_M1_defaults(self):
        for suffix in (b'', b'output_parent="outputs"\n', b'parameters=[]\n'):
            result = self.discover(MINIMAL + suffix)
            self.assertEqual(result['parent'], str(self.project / 'outputs'))
            self.assertEqual(result['argv'], [])
            self.assertEqual(result['binding'], 'unverified')

    def test_M2_custom_declaration_behavior(self):
        metadata = MINIMAL + b'output_parent="results/nested"\n'
        result = self.discover(metadata)
        # Deliberate fixture adoption aligns the authored parser default as well.
        p = self.project / 'simulate.py'
        p.write_text(p.read_text().replace("default='outputs'", "default='results/nested'"))
        self.assertEqual(str(self.run_root().parent), result['parent'])

    def test_M3_bound_external(self):
        argv = ['--output-parent', str(self.external)]
        result = self.discover(MINIMAL + BINDING, argv)
        self.assertEqual(result['parent'], str(self.run_root(argv).parent))
        self.assertEqual(result['token_spans'], [[0, 2]])

    def test_M4_forms(self):
        dest = str(self.external / 'with space=literal')
        for argv in (['--output-parent', dest], ['--output-parent=' + dest], ['-o', dest]):
            result = self.discover(MINIMAL + BINDING, argv)
            self.assertEqual(result['argv'], argv)
            self.assertEqual(str(self.run_root(argv).parent), result['parent'])

    def test_M5_metadata_paths(self):
        for value in ('', '/absolute', '../escape', 'a/', 'a//b', './a', 'a\\b', 'C:drive', 'uri:path', '~', '$X', '*', '?', '[x]', '\x01', 'x'*1025):
            with self.subTest(value=value), self.assertRaises(ValueError):
                contract.parse(MINIMAL + ('output_parent=' + json.dumps(value) + '\n').encode())
        contract.parse(MINIMAL + ('output_parent="' + 'x'*1024 + '"\n').encode())

    def test_M6_binding_errors(self):
        original = MINIMAL + BINDING
        for old, new in ((b'"destination"', b'9'), (b'"destination"', b'"missing"'),
                         (b'kind = "option"', b'kind = "positional"'), (b'type = "string"', b'type = "boolean"'),
                         (b'type = "string"', b'type = "integer"'), (b'required = false', b'required = true'),
                         (b'default = "outputs"', b'default = "elsewhere"'),
                         (b'default = "outputs"', b'repeatable = true'),
                         (b'default = "outputs"', b'choices = ["outputs"]'),
                         (b'["--output-parent", "-o"]', b'["-o", "-o"]')):
            with self.subTest(new=new), self.assertRaises(ValueError): contract.parse(original.replace(old, new, 1))
        with self.assertRaises(ValueError): contract.parse(original + b'\n[[swss.parameters]]' + BINDING.split(b'[[swss.parameters]]')[1])

    def test_M7_unresolved_argv(self):
        for argv in (['-o','x','-o','x'], ['-o'], ['-o',''], ['-o','--unknown'], ['-ox'], ['-ab'],
                     ['--unknown'], ['--','-o','x'], ['-o=x']):
            before = list(argv)
            with self.subTest(argv=argv), self.assertRaises(ValueError): self.discover(MINIMAL + BINDING, argv)
            self.assertEqual(argv, before)

    def test_M8_no_inferred_binding(self):
        with self.assertRaises(ValueError): self.discover(MINIMAL, ['--output-parent', 'somewhere'])
        unbound = MINIMAL + BINDING.replace(b'output_parent_parameter = "destination"\n', b'')
        self.assertEqual(self.discover(unbound, ['-o', 'somewhere'])['parent'], str(self.project / 'outputs'))
        self.assertNotEqual(str(self.run_root(['-o','somewhere']).parent), self.discover(unbound, ['-o','somewhere'])['parent'])

    def test_M9_other_controls(self):
        data = (self.project / 'swss.toml').read_bytes()
        sources = {n: (self.project / n).read_bytes() for n in ('simulate.py', 'output_contract.py')}
        argv = ['-k','1e-1','-n','0010','--label','','--no-series','--progress']
        result = self.discover(data, argv, sources=sources)
        self.assertEqual(result['argv'], argv)
        self.assertEqual(result['parent'], str(self.project / 'outputs'))

    def test_M10_local_conflict(self):
        with self.assertRaises(ValueError): self.discover(local='elsewhere')
        self.discover(local=str(self.project / 'outputs'))

    def test_M11_preview_changes(self):
        first = self.discover()
        changed = self.discover(MINIMAL + b'[extensions.note]\ntext="new"\n')
        self.assertNotEqual(first['metadata_sha256'], changed['metadata_sha256'])
        self.assertNotEqual(first['parent'], self.discover(MINIMAL + BINDING, ['-o','other'])['parent'])
        elsewhere = contract.resolve_parent(MINIMAL, [], self.other, 'simulate.py')
        self.assertNotEqual(first['parent'], elsewhere['parent'])
        self.test_N7_stale_unassociated()
        with self.assertRaises(ValueError): self.discover(local='conflict')
        manifest = MINIMAL + b'[[swss.source_files]]\npath="simulate.py"\nsha256="' + b'0'*64 + b'"\n'
        with self.assertRaises(ValueError): self.discover(manifest, sources={'simulate.py': b'x'*(16*1024**2+1)})

    def test_M12_reader_compatibility(self):
        for metadata in (MINIMAL, MINIMAL + BINDING):
            with self.assertRaisesRegex(ValueError, 'unsupported schema'): contract.parse(metadata, supported=(2,))
        legacy = MINIMAL.replace(b'= 3', b'= 2')
        contract.parse(legacy)
        with self.assertRaisesRegex(ValueError, 'no automatic'): self.discover(legacy)
        with self.assertRaises(ValueError): contract.parse(MINIMAL.replace(b'= 3', b'= 4'))
        # Exercise the preserved actual schema-2 author reader too.
        import importlib.util
        spec = importlib.util.spec_from_file_location('legacy_check', ROOT.parent / 'decay-v2/check_contract.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        legacy_source = (ROOT.parent / 'decay-v2/simulate.py').read_bytes()
        legacy_meta = (ROOT.parent / 'decay-v2/swss.toml').read_bytes()
        self.assertEqual(module.compare(legacy_source, legacy_meta), 12)
        with self.assertRaises(ValueError): module.compare(legacy_source, legacy_meta.replace(b'schema_version = 2', b'schema_version = 3'))

    def test_M13_no_discovery_side_effects(self):
        with patch('builtins.open', side_effect=AssertionError('open')), \
             patch('pathlib.Path.stat', side_effect=AssertionError('stat')), \
             patch('pathlib.Path.mkdir', side_effect=AssertionError('mkdir')), \
             patch('subprocess.Popen', side_effect=AssertionError('execute')), \
             patch('socket.socket', side_effect=AssertionError('network')), \
             patch('builtins.exec', side_effect=AssertionError('exec')):
            self.discover(MINIMAL + BINDING, ['-o', str(self.external)])
            self.discover(MINIMAL + b'output_parent="absent/new"\n')
            self.discover(MINIMAL + b'[extensions.note]\ntext="$(execute nothing)"\n')
        self.assertFalse(self.external.exists())

    def test_M14_exclusion_precedence(self):
        custom = self.project / 'results'
        custom.mkdir()
        (custom / 'generated.py').write_bytes(b'not source')
        result = self.discover(MINIMAL + b'output_parent="results"\n' + BINDING.replace(b'"outputs"', b'"results"'), ['-o', str(self.external)])
        snap = self.snap(custom, Path(result['parent']))
        self.assertFalse(any(k.startswith(('results/', 'outputs/')) for k in snap))
        self.assertIn('outputs_notes/analysis.py', snap)

    def test_M15_declaration_not_behavior(self):
        source = (self.project / 'simulate.py').read_bytes()
        declared = MINIMAL + b'output_parent="declared"\n[[swss.source_files]]\npath="simulate.py"\nsha256="' + hashlib.sha256(source).hexdigest().encode() + b'"\n'
        result = self.discover(declared, sources={'simulate.py': source})
        self.assertEqual(result['binding'], 'listed bytes match; behavior unverified')
        self.assertNotEqual(str(self.run_root().parent), result['parent'])
        # Schema-number-only edits cannot change a legacy cwd-relative program.
        legacy = self.base / 'legacy'
        shutil.copytree(ROOT.parent / 'decay-v2', legacy)
        p = legacy / 'swss.toml'
        p.write_bytes(p.read_bytes().replace(b'schema_version = 2', b'schema_version = 3'))
        proc = subprocess.run([sys.executable, '-B', str(legacy / 'simulate.py'), '--rate','1'], cwd=self.other, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.other / 'outputs').exists())
        self.assertFalse((legacy / 'outputs').exists())


class SchemaRegressionTests(unittest.TestCase):
    def test_invalid_document_shapes_and_bounds(self):
        for extra in (b'unknown="x"', b'output_parent=2', b'output_parent_parameter=true',
                      b'parameters={}', b'source_files=[]', b'source_files={}',
                      b'[[parameters]]', b'[swss.bad]\nx=1', b'[extensions]\nx=1',
                      b'[extensions.BAD]\nx=1', b'[extensions.x]\nx=inf',
                      b'[extensions.x]\nx="' + b'x'*4097 + b'"'):
            with self.subTest(extra=extra[:70]), self.assertRaises(ValueError):
                contract.parse(MINIMAL + extra)
        for version in (b'true', b'"3"', b'3.0', b'4'):
            with self.assertRaises(ValueError): contract.parse(MINIMAL.replace(b'= 3', b'= ' + version))
        with self.assertRaises(ValueError): contract.parse(MINIMAL + b'#' * 16385)
        with self.assertRaises(ValueError): contract.parse(MINIMAL + b'schema_version=3')

    def test_manual_row_is_not_routing_authority(self):
        unbound = (MINIMAL + BINDING).replace(b'output_parent_parameter = "destination"\n', b'')
        for edit in (b'nargs="+"', b'repeatable=true', b'action="append"'):
            changed = unbound + edit if not edit.startswith(b'action=') else unbound.replace(b'action = "store"', edit)
            _, manual = contract.parse(changed)
            self.assertEqual(manual, {'destination'})
            with self.assertRaises(ValueError):
                contract.resolve_parent(changed, ['-o','x'], Path('/project'), 'simulate.py')
        with self.assertRaises(ValueError): contract.parse(unbound + b'unknown={nested=1}')
        with self.assertRaises(ValueError): contract.parse(unbound + b'unknown=2026-10-29')

    def test_numeric_grammar_and_row_types(self):
        base = (MINIMAL + BINDING).replace(b'output_parent_parameter = "destination"\n', b'').replace(b'default = "outputs"', b'')
        for kind, valid, invalid in ((b'integer', '0010', '1.0'), (b'float', '-1e-3', 'nan')):
            meta = base.replace(b'type = "string"', b'type = "' + kind + b'"')
            result = contract.resolve_parent(meta, ['-o', valid], Path('/project'), 'simulate.py')
            self.assertEqual(result['argv'], ['-o', valid])
            with self.assertRaises(ValueError): contract.resolve_parent(meta, ['-o', invalid], Path('/project'), 'simulate.py')
        for default in (b'true', b'1', b'1.0'):
            _, manual = contract.parse(base + b'default=' + default)
            self.assertEqual(manual, {'destination'})

    def test_source_alias_and_read_budget(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'source'
            p.write_bytes(b'bytes')
            alias = Path(d) / 'alias'
            alias.symlink_to(p)
            with self.assertRaises(ValueError): contract.read_source(alias)
            with self.assertRaises(ValueError): contract.read_source(p, limit=4)
            self.assertEqual(contract.read_source(p), b'bytes')


if __name__ == '__main__': unittest.main()

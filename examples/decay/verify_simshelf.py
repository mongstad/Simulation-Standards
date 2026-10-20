# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Optional API integration check; needs an explicitly selected SimShelf environment."""
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path


def main():
    from fastapi.testclient import TestClient
    from simshelf.api import create_app
    from simshelf.store import Store
    from simshelf.source import blob_path
    from simshelf.capture import preview
    from simshelf._version import __version__
    source = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='swss-consumer-') as temp:
        root = Path(temp) / 'simulation'
        shutil.copytree(source, root, ignore=shutil.ignore_patterns('outputs', '__pycache__'))
        store = Store(Path(temp) / 'library')
        sim = store.add_simulation(root, entrypoint='simulate.py')
        base = f"/api/simulations/{sim['id']}"
        original = (root / 'swss.toml').read_bytes()
        argv = ['-k', '1e-1', '-n', '0010', '--label', '', '--no-series']
        config = {'interpreter': sys.executable, 'cwd': '.', 'arguments': argv,
                  'output_dir': 'outputs/fixed', 'output_policy': 'fixed'}
        with TestClient(create_app(store.path)) as client:
            auth = {'X-SimShelf-Token': client.get('/api/workspace').json()['token']}
            discovery = client.get(base + '/parameters').json()
            rows = discovery['parameters']
            assert len(rows) == 12 and all(row['supported'] for row in rows), discovery
            by_name = {r['name']: r for r in rows}
            assert by_name['--rate']['required'] and not by_name['--rate']['default_known']
            assert not by_name['--dt']['default_known']
            assert by_name['--steps']['default'] == 20
            assert by_name['--rate-scale']['choices'] == [.5, 1.0, 2.0]
            assert by_name['--label']['default'] == ''
            assert by_name['--progress']['default'] is False
            assert by_name['--no-series']['default'] is True
            assert discovery['provenance']['binding_status'] == 'listed bytes verified'
            config['parameter_review'] = {'mode': 'typed', 'fingerprint': discovery['fingerprint']}
            saved = client.put(base + '/execution', headers=auth, json=config)
            assert saved.status_code == 200, saved.text
        # Reopen the application/store, not just a JSON round trip in test code.
        store = Store(store.path)
        assert store.simulation(sim['id'])['execution']['arguments'] == argv
        with TestClient(create_app(store.path)) as client:
            auth = {'X-SimShelf-Token': client.get('/api/workspace').json()['token']}
            assert client.get(base + '/parameters').json()['fingerprint'] == discovery['fingerprint']
            (root/'outputs/fixed').mkdir(parents=True)
            results = []
            prior_bytes = {}

            def launch(settings):
                response = client.post(base + '/launch', headers=auth, json=settings)
                assert response.status_code == 201, response.text
                return response.json()['run_id']

            def verify(run_id, settings):
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    run = store.run(run_id)
                    if run['status'] != 'running':
                        break
                    time.sleep(.05)
                assert run['status'] == 'completed', run
                assert run['capture_status'] == 'complete' and not run['capture_errors'], run
                actual_argv = settings['arguments']
                assert run['command'][2:] == actual_argv
                evidence = run['parameter_metadata']
                assert evidence['argv'] == actual_argv
                assert evidence['provenance']['bytes_utf8'].encode() == original
                run_root = root / run['capture_config']['output_dir']
                if settings['output_policy'] == 'per_run':
                    assert run_root.parent == root/'outputs'
                    assert run_root.name == 'run_' + run_id
                assert not any(p.is_dir() for p in run_root.iterdir()), run_root
                provenance = json.loads((run_root/'provenance.json').read_text())
                assert provenance['argv'] == actual_argv and provenance['simulation_version'] == '0.1.1'
                assert provenance['output_directory'] == str(run_root)
                assert provenance['output_allocation'] == 'coordinated'
                assert run['version'] == 'unversioned'  # Consumer-specific version-tag limitation.
                expected = {'summary.json', 'provenance.json', next(run_root.glob('*.log')).name}
                if '--no-series' not in actual_argv:
                    expected.add('measurements.csv')
                copied = [a for a in run['artifacts'] if a['policy'] == 'copy']
                assert {a['name'] for a in copied} == expected, run['artifacts']
                eligibility = preview({**sim, 'config': run['capture_config']})
                assert not eligibility['errors']
                assert all(f['action'] == 'copy' and f['reason'] is None
                           for f in eligibility['files'] if f['path'] in expected)
                for artifact in copied:
                    assert blob_path(store.path, artifact['blob']).read_bytes() == (run_root/artifact['name']).read_bytes()
                logdir = store.path/'logs'/run_id
                assert str(run_root) in (logdir/'stdout.log').read_text()
                assert (logdir/'stderr.log').is_file()
                paths = {f['path'] for f in run['snapshot']['files']}
                assert {'simulate.py', 'swss.toml'} <= paths
                assert not any(p.startswith('outputs/') for p in paths)
                for path, data in prior_bytes.items():
                    assert path.read_bytes() == data
                prior_bytes.update({p: p.read_bytes() for p in run_root.iterdir()})
                results.append({'policy': settings['output_policy'], 'copied_artifacts': len(copied),
                                'status': run['status'], 'capture_status': run['capture_status']})
                return run_root

            verify(launch(config), config)
            # Two launches before waiting, plus a successive run without the CSV.
            coordinated = {**config, 'output_policy': 'per_run', 'output_dir': 'outputs',
                           'arguments': argv[:-1]}
            ids = [launch(coordinated) for _ in range(2)]
            roots = [verify(ident, coordinated) for ident in ids]
            assert roots[0] != roots[1]
            assert (roots[0]/'measurements.csv').read_bytes() == (roots[1]/'measurements.csv').read_bytes()
            no_series = {**coordinated, 'arguments': argv}
            verify(launch(no_series), no_series)
            # Invalid metadata and stale binding both leave the saved argv usable manually.
            for bad in (original + b'\n[swss]\n', original.replace(b'sha256 = "', b'sha256 = "0', 1)):
                (root/'swss.toml').write_bytes(bad)
                invalid = client.get(base + '/parameters').json()
                assert not invalid['parameters'] and invalid['warnings'], invalid
                manual = {**config, 'parameter_review': {'mode': 'manual', 'fingerprint': None}}
                response = client.put(base + '/execution', headers=auth, json=manual)
                assert response.status_code == 200, response.text
                assert store.simulation(sim['id'])['execution']['arguments'] == argv
            (root/'swss.toml').write_bytes(original)
            (root/'simulate.py').write_bytes((root/'simulate.py').read_bytes() + b'\n# stale test\n')
            stale = client.get(base + '/parameters').json()
            assert not stale['parameters'] and stale['provenance']['binding_status'] == 'stale / manual-only'
        print(json.dumps({'consumer': 'SimShelf', 'version': __version__, 'rows': len(rows),
                          'runs': results,
                          'checks': ['defaults', 'save/reopen', 'exact argv', 'metadata provenance',
                                     'direct coordinated output', 'capture eligibility', 'copied artifact bytes',
                                     'separate stdout/stderr', 'source snapshot exclusions',
                                     'manual fallback', 'stale binding'],
                          'limits': ['API only; no browser UI verification',
                                     'consumer version label is unversioned; simulation provenance retains 0.1.1',
                                     'fixed directory precreated; repeated use must fail rather than overwrite']}))


if __name__ == '__main__':
    main()

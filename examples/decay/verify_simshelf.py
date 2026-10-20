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
                  'output_dir': 'outputs', 'output_policy': 'fixed'}
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
            response = client.post(base + '/launch', headers=auth, json=config)
            assert response.status_code == 201, response.text
            run_id = response.json()['run_id']
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                run = store.run(run_id)
                if run['status'] != 'running':
                    break
                time.sleep(.05)
            assert run['status'] == 'completed', run
            assert run['command'][2:] == argv
            evidence = run['parameter_metadata']
            assert evidence['argv'] == argv
            assert evidence['provenance']['bytes_utf8'].encode() == original
            run_root, = (root / 'outputs').iterdir()
            provenance = json.loads((run_root/'provenance.json').read_text())
            assert provenance['argv'] == argv and provenance['simulation_version'] == '0.1.0'
            assert run['version'] == 'unversioned'  # Consumer-specific version-tag limitation.
            copied = [a for a in run['artifacts'] if a['policy'] == 'copy']
            assert any(a['name'].endswith('.log') for a in copied), run
            for artifact in copied:
                actual = root / 'outputs' / artifact['name']
                assert blob_path(store.path, artifact['blob']).read_bytes() == actual.read_bytes()
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
                          'status': run['status'], 'copied_artifacts': len(copied),
                          'checks': ['defaults', 'save/reopen', 'exact argv', 'metadata provenance',
                                     'copied artifact bytes', 'manual fallback', 'stale binding'],
                          'limits': ['API only; no browser UI verification',
                                     'consumer version label is unversioned; simulation provenance retains 0.1.0',
                                     'fixed capture; coordinated capture not claimed']}))


if __name__ == '__main__':
    main()

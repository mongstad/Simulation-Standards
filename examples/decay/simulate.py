# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Small scalar decay model; see README.md for equations and evidence limits."""
import argparse
import csv
import hashlib
import json
import math
import platform
import signal
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

from output_contract import identities, read_source, recheck, runtime_path, validate_parent

VERSION = "0.1.4"

# Author-selected root for this root-level reference deployment, independent of cwd.
SIMULATION_ROOT = Path(__file__).absolute().parent


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    p.add_argument('--rate', '-k', type=float, required=True, help='Positive decay rate in inverse time units')
    p.add_argument('--initial', '-c', type=float, default=1.0, help='Initial concentration in mol/L; must be positive')
    p.add_argument('--steps', '-n', type=int, choices=[10, 20, 40], default=20, help='Number of integration steps')
    p.add_argument('--dt', type=float, default=None, help='Time advanced per step; omitted value resolves from rate and steps')
    p.add_argument('--method', type=str, choices=['euler', 'exact'], default='euler', help='Integration rule for the decay equation')
    p.add_argument('--sample-every', type=int, choices=[1, 2, 5], default=1, help='Step interval for saved measurements; final state is always sampled')
    p.add_argument('--rate-scale', type=float, choices=[0.5, 1.0, 2.0], default=1.0, help='Dimensionless multiplier applied to the decay rate')
    p.add_argument('--time-unit', type=str, choices=['s', 'min'], default='s', help='Unit used consistently for time and inverse decay rate; no conversion')
    p.add_argument('--label', type=str, default='', help='Free-text run annotation; empty text is meaningful')
    p.add_argument('--output-parent', '-o', type=str, default='outputs', help='Parent for a new unique run directory; relative to the selected simulation root')
    p.add_argument('--progress', action='store_true', default=False, help='Emit measured step counts and concentration at sample times')
    p.add_argument('--no-series', dest='series', action='store_false', default=True, help='Omit the measurement series while retaining the final diagnostic')
    return p


def resolve(args):
    config = vars(args).copy()
    for name in ('rate', 'initial'):
        if not math.isfinite(config[name]) or config[name] <= 0:
            raise ValueError(f'{name} must be finite and positive')
    effective_rate = args.rate * args.rate_scale
    if not math.isfinite(effective_rate) or effective_rate <= 0:
        raise ValueError('effective rate must be finite and positive')
    dt = args.dt if args.dt is not None else (0.5 / effective_rate) / args.steps
    if not math.isfinite(dt) or dt <= 0 or not math.isfinite(dt * args.steps):
        raise ValueError('dt and final time must be finite and positive')
    if not math.isfinite(effective_rate * dt) or effective_rate * dt > 1:
        raise ValueError('effective rate * dt must be <= 1 for this reference model')
    config.update(dt=dt, effective_rate=effective_rate)
    return config


def advance(value, rate, dt, method):
    """No I/O, RNG or instrumentation in the numerical step."""
    factor = 1 - rate * dt if method == 'euler' else math.exp(-rate * dt)
    result = value * factor
    if not math.isfinite(result):
        raise ArithmeticError('nonfinite concentration')
    return result


def diagnostic(config, step, value):
    time = step * config['dt']
    reference = config['initial'] * math.exp(-config['effective_rate'] * time)
    error = abs(value - reference)
    if not all(math.isfinite(x) for x in (time, reference, error, value)):
        raise ArithmeticError('nonfinite diagnostic')
    return {'step': step, 'time': time, 'concentration': value,
            'analytic_concentration': reference, 'absolute_error': error}


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False, ensure_ascii=False)
        stream.write('\n')


def output_directory(config, stamp, run_id):
    """Exclusively allocate one standalone run directory beneath the parent."""
    selected = Path(config.get('simulation_root', SIMULATION_ROOT))
    parent = runtime_path(selected, config['output_parent'])
    # This fixture has no external scientific inputs. Protect the whole source
    # package's non-output files by rejecting a parent containing any such file.
    protected = [selected / name for name in ('simulate.py', 'swss.toml', 'output_contract.py',
                 'check_contract.py', 'README.md', 'VALIDATION.md', 'tests', 'inputs', 'solver')]
    protected.extend(Path(__file__).absolute().parent / name
                     for name in ('simulate.py', 'output_contract.py'))
    guards = validate_parent(selected, parent, protected)
    recheck(guards)
    parent.mkdir(parents=True, exist_ok=True)
    recheck(guards)
    guards = identities(parent)
    recheck(guards)
    root = parent / f'run_{stamp}_{run_id}'
    root.mkdir()  # Atomic exclusive allocation; never reuse an occupied root.
    return root


def run(config, argv):
    started = datetime.now(timezone.utc)
    run_id = uuid.uuid4().hex  # Independent of any scientific RNG.
    stamp = started.strftime('%Y%m%dT%H%M%SZ')
    root = output_directory(config, stamp, run_id)
    log_name = f'run_{stamp}_v{VERSION}_{run_id}.log'
    source_root = Path(config.get('simulation_root', SIMULATION_ROOT))
    package_root = Path(__file__).absolute().parent
    status, code, final = 'failed', 1, None
    with (root / log_name).open('x', encoding='utf-8') as log:
        log.write(f'version={VERSION} run_id={run_id} status=running\n')
        log.write(f'output_directory={root.absolute()}\n')
        log.write('argv=' + json.dumps(argv, ensure_ascii=False) + '\n')
        log.write('resolved=' + json.dumps(config, allow_nan=False) + '\n')
        log.flush()
        try:
            source = {str((package_root / name).relative_to(source_root)):
                      hashlib.sha256(read_source(package_root / name)).hexdigest()
                      for name in ('simulate.py', 'output_contract.py')}
            if (source_root / 'swss.toml').exists():
                source['swss.toml'] = hashlib.sha256(read_source(source_root / 'swss.toml', 16384)).hexdigest()
            write_json(root / 'provenance.json', {
                'simulation': 'scalar-decay', 'simulation_version': VERSION,
                'swss_version': '3.0', 'run_id': run_id, 'started_utc': started.isoformat(),
                'argv': list(argv), 'resolved': config, 'source_sha256': source,
                'output_directory': str(root.absolute()),
                'simulation_root': str(source_root), 'effective_output_parent': str(root.parent),
                'selected_entrypoint': str((package_root / 'simulate.py').relative_to(source_root)),
                'allocation_mode': 'standalone child',
                'known_output_boundaries': [str(source_root / 'outputs'), str(root.parent)],
                'path_check_timing': 'before parent creation and exclusive child allocation',
                'source_policy': 'explicit package files only; no recursive output/source discovery',
                'source_observation': 'bytes at run startup; no process isolation',
                'python': platform.python_version(), 'implementation': platform.python_implementation(),
                'platform': platform.platform(), 'dependencies': 'Python standard library only',
                'precision': 'Python float (binary64 on tested CPython)',
                'rng': 'none', 'grid': None, 'boundary_conditions': 'not applicable: scalar ODE',
                'external_inputs': [], 'restart_lineage': None,
                'units': {'time': config['time_unit'], 'rate': '1/' + config['time_unit'],
                          'concentration': 'mol/L', 'absolute_error': 'mol/L', 'rate_scale': 'dimensionless'},
                'files': {'log': log_name, 'summary': 'summary.json',
                          'measurements': 'measurements.csv' if config['series'] else None},
            })
            series = None
            try:
                if config['series']:
                    series = (root / 'measurements.csv').open('x', newline='', encoding='utf-8')
                    writer = csv.DictWriter(series, fieldnames=list(diagnostic(config, 0, config['initial'])))
                    writer.writeheader()
                value = config['initial']
                for step in range(config['steps'] + 1):
                    if step:
                        value = advance(value, config['effective_rate'], config['dt'], config['method'])
                    if step % config['sample_every'] == 0 or step == config['steps']:
                        final = diagnostic(config, step, value)
                        if series:
                            writer.writerow(final)
                        if config['progress']:
                            print(json.dumps({'adapter': 'decay-progress-v1', 'current': step,
                                              'total': config['steps'], **final}), flush=True)
            finally:
                if series:
                    series.close()
            status, code = 'completed', 0
        except KeyboardInterrupt:
            status, code = 'cancelled', 130
            log.write('Interrupted; partial evidence retained.\n')
        except Exception:
            traceback.print_exc(file=log)
        # A failure writing/closing evidence propagates to a nonzero process exit.
        write_json(root / 'summary.json', {
            'run_id': run_id, 'status': status, 'last_sample': final,
            'output_directory': str(root.absolute()),
            'quantities': {'physically_modeled': ['concentration'],
                           'diagnostic': ['analytic_concentration', 'absolute_error'],
                           'dimensionless': ['step']},
            'verified': False,  # Completion is not independent numerical verification.
        })
        log.write(f'status={status} exit_code={code}\n')
    print(f'run_directory={root}', flush=True)
    return code


def main(argv=None, *, simulation_root=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = resolve(args)
        selected = Path(simulation_root) if simulation_root is not None else SIMULATION_ROOT
        if not selected.is_absolute() or not selected.is_dir():
            raise ValueError('simulation root must be an explicitly selected absolute directory')
        identities(selected)
        if not Path(__file__).absolute().is_relative_to(selected):
            raise ValueError('selected entrypoint is outside the simulation root')
        config['simulation_root'] = str(selected)
    except ValueError as error:
        parser.error(str(error))
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupted)
    try:
        return run(config, argv)
    except (OSError, ValueError) as error:
        print(f'run/evidence failure: {error}', file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == '__main__':
    raise SystemExit(main())

# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Small scalar decay model; see README.md for equations and evidence limits."""
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import signal
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.1"


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
    p.add_argument('--output-parent', type=str, default='outputs', help='Parent for a new unique run directory; relative to the working directory')
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


def output_directory(config, argv, stamp, run_id):
    """Use the recorder's exact root, or allocate a standalone root."""
    if 'SIMSHELF_OUTPUT_DIR' not in os.environ:
        parent = Path(config['output_parent'])
        parent.mkdir(parents=True, exist_ok=True)
        root = parent / f'run_{stamp}_{run_id}'
        root.mkdir()  # Atomic exclusive allocation; never reuse an occupied root.
        return root, 'standalone'
    # Defaults do not indicate explicit user intent. Abbreviations are disabled.
    tokens = argv[:argv.index('--')] if '--' in argv else argv
    if any(token == '--output-parent' or token.startswith('--output-parent=') for token in tokens):
        raise ValueError('explicit --output-parent conflicts with SIMSHELF_OUTPUT_DIR')
    root = Path(os.environ['SIMSHELF_OUTPUT_DIR'])
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError('SIMSHELF_OUTPUT_DIR must be an absolute, existing directory (not a symlink)')
    if not os.access(root, os.R_OK | os.W_OK | os.X_OK):
        raise ValueError('SIMSHELF_OUTPUT_DIR must be readable, writable and searchable')
    if any(root.iterdir()):
        raise ValueError('SIMSHELF_OUTPUT_DIR must be empty and unused for this run')
    # Persist an exclusive claim: two processes cannot share a preallocated root,
    # even if both observed it empty. Never remove the claim or partial evidence.
    with (root / '.swss-run').open('x', encoding='utf-8') as claim:
        claim.write(run_id + '\n')
    return root, 'coordinated'


def run(config, argv):
    started = datetime.now(timezone.utc)
    run_id = uuid.uuid4().hex  # Independent of any scientific RNG.
    stamp = started.strftime('%Y%m%dT%H%M%SZ')
    root, allocation = output_directory(config, argv, stamp, run_id)
    log_name = f'run_{stamp}_v{VERSION}_{run_id}.log'
    source_root = Path(__file__).resolve().parent
    status, code, final = 'failed', 1, None
    with (root / log_name).open('x', encoding='utf-8') as log:
        log.write(f'version={VERSION} run_id={run_id} status=running\n')
        log.write(f'output_directory={root.absolute()} allocation={allocation}\n')
        log.write('argv=' + json.dumps(argv, ensure_ascii=False) + '\n')
        log.write('resolved=' + json.dumps(config, allow_nan=False) + '\n')
        log.flush()
        try:
            source = {name: hashlib.sha256((source_root / name).read_bytes()).hexdigest()
                      for name in ('simulate.py', 'swss.toml')}
            write_json(root / 'provenance.json', {
                'simulation': 'scalar-decay', 'simulation_version': VERSION,
                'swss_version': '2.0', 'run_id': run_id, 'started_utc': started.isoformat(),
                'argv': list(argv), 'resolved': config, 'source_sha256': source,
                'output_directory': str(root.absolute()), 'output_allocation': allocation,
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
            'quantities': {'physically_modeled': ['concentration'],
                           'diagnostic': ['analytic_concentration', 'absolute_error'],
                           'dimensionless': ['step']},
            'verified': False,  # Completion is not independent numerical verification.
        })
        log.write(f'status={status} exit_code={code}\n')
    print(f'run_directory={root}', flush=True)
    return code


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = resolve(args)
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

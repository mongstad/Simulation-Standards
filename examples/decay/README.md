# Scalar decay reference

A small, independently executable Python 3.11+ simulation for checking the [SWSS v2.0](../../standards/SWSS/v2.0.md) baseline and simulation-authored portable metadata. It uses only the Python standard library. Twelve purposeful controls exercise required values, aliases, integer/float/string choices, known and context-dependent defaults, Boolean flags and empty strings. It is a numerical workflow fixture, not a validated model of a particular experiment.

## Run and verify

From this directory:

```bash
python -B simulate.py -k 1e-1 -n 0010 --dt=0.25 --label ''
python -B check_contract.py
python -B -m unittest discover -s tests -v
```

Each run writes a new `outputs/run_<UTC timestamp>_<UUID>/` directory relative to the working directory. `--output-parent` selects another parent, never an existing run directory to overwrite. Output allocation and individual file creation are exclusive; a collision fails without selecting a replacement. Success prints the run directory and exits zero. Argument/domain errors exit 2 before a run starts. Handled computation failures exit 1; SIGINT/SIGTERM during computation exit 130. Partial evidence remains. Output allocation or storage failures exit nonzero; failure before logging is possible and is reported on stderr. Forced termination or full storage can leave incomplete evidence. Process success, summary completion and independent scientific verification are separate.

The directory contains a timestamped/versioned `.log`, `provenance.json`, `summary.json`, and normally `measurements.csv`. The log records version, run ID, argv, resolved configuration and status/errors. Provenance records the exact argument tokens separately from resolved values, source/configuration SHA-256 values observed at startup, runtime/platform, units, effective output directory, output names and scientific assumptions. UUID generation does not influence the solver. No RNG, external scientific inputs, spatial grid, boundary conditions or restart state are used. Source hashing observes files at startup; it does not isolate a running process from later edits. Retain the corresponding source bytes with research evidence; hashes alone are not a backup.

## Model and controls

The scalar concentration obeys `dc/dt = -k_eff c`, with `k_eff = rate × rate_scale`. Concentration is in mol/L. Time uses the selected `s` or `min`; rate is in the reciprocal unit. Selecting a unit labels the supplied numerical values consistently; it does not convert them. Initial concentration and rate must be finite and positive.

Euler uses `c[n+1] = c[n] × (1 - k_eff × dt)`. The exact-step alternative uses `c[n+1] = c[n] × exp(-k_eff × dt)`. Both enforce `0 < k_eff × dt <= 1` for this fixture. If omitted, `dt = (0.5 / k_eff) / steps`; its resolved value therefore depends on other parameters and no default is declared in TOML. Final time must be finite. Computation uses Python floats and system `exp`; rounding and underflow can vary across platforms. Cross-platform byte identity is not promised.

| Option (alias) | Meaning / default |
| --- | --- |
| `--rate` (`-k`) | Required positive decay rate; no default. |
| `--initial` (`-c`) | Initial concentration; 1.0 mol/L. |
| `--steps` (`-n`) | Integration steps: 10, 20 or 40; default 20. |
| `--dt` | Step duration; context-dependent when omitted. |
| `--method` | `euler` or `exact`; default `euler`. |
| `--sample-every` | Save every 1, 2 or 5 steps; default 1. Initial and final state always sampled. |
| `--rate-scale` | Dimensionless sensitivity multiplier: 0.5, 1.0 or 2.0; default 1.0. |
| `--time-unit` | `s` or `min`; default `s`. |
| `--label` | Free text; known empty-string default. |
| `--output-parent` | Parent directory; default `outputs`. |
| `--progress` | `store_true`: emit sample telemetry when present; default false. |
| `--no-series` | `store_false`: disable CSV when present; series default true. |

The script's parser is authoritative. The TOML is a separately maintained declaration, never loaded to configure the solver or generate its parser. `--help` is an argparse control, not a scientific parameter, and is not declared. Omitted options do not become argv tokens. For example `-n 0010` remains those two tokens in provenance although the resolved step count is 10; `--label ''` records an explicit empty token. Repeated scalar options retain their original argv but argparse resolves the last occurrence. Unknown options and positional values fail in this model; consumer manual fallback does not promise parser acceptance.

## Diagnostics and optional capabilities

At sampled solver times `t = n × dt`, the CSV stores `step`, `time`, `concentration`, `analytic_concentration = initial × exp(-k_eff × t)`, and `absolute_error = abs(concentration - analytic_concentration)`. The last three quantities use mol/L. These are source-state samples and an analytic diagnostic, not interpolated display values. Nonfinite values cause failure. CSV uses Python's ordinary decimal float representation and UTF-8; tests read it with `csv.DictReader` and compare against independent closed-form expressions. The final diagnostic remains in the summary when `--no-series` is enabled. A run never labels itself independently verified.

`--progress` emits JSON lines using the illustrative local `decay-progress-v1` adapter (not a normative SWSS transport): `current`/`total` count completed integration steps (initial state is zero), plus the sampled diagnostic fields above. At most 41 messages occur. A final step count is not a completion or capture assertion. Final diagnostics are independently saved; the complete series is saved unless explicitly disabled. No recorder-side metric transport, retention or overhead benchmark is claimed. Instrumentation tests compare final values with telemetry/series enabled and disabled.

The fixture implements baseline behavior and supplies schema-2 author declarations. It is **not a portable metadata consumer or editor**, and does not claim full consumer conformance. It does not implement the optional §3.1 coordinated-capture capability: each invocation allocates its own unique root, rather than accepting a launcher-assigned run root. It does not implement a universal scientific-export adapter, checkpoint/resume or a viewer. Ordinary CSV diagnostics are baseline evidence. The optional telemetry emitter covers the simulation side only; full §3.2 recorder conformance is untested. See [validation evidence and limitations](VALIDATION.md).

## Contract maintenance and negative fixtures

`swss.toml` is the only companion configuration, with entrypoint `simulate.py`. Its optional source manifest binds only the exact bytes of `simulate.py`; it does not claim to bind the entire package or prove semantics. Tests verify the actual parser's aliases, types, actions, requiredness, choices and defaults against all twelve declarations. The current source version is `0.1.3` (standalone output allocation); before the next recorded run after an accepted source-package change, bump `VERSION` and `swss.simulation_version` together (including metadata, documentation or instrumentation changes), then refresh the source hash and rerun checks. Argument changes alone do not bump source version.

Print the new digest with `python -c 'import hashlib; print(hashlib.sha256(open("simulate.py", "rb").read()).hexdigest())'`, then deliberately update `swss.source_files`. Do not hash `swss.toml` inside itself. Run provenance separately hashes the actual TOML bytes. Nothing automatically rewrites scientific source or metadata.

`check_contract.py` is an offline author tool specialized to this fixture's literal `build_parser` declarations. It reads at most 64 KiB per file, parses source syntax without execution and compares it with TOML. It does not import the checked source, discover arbitrary projects, supply UI controls, or implement the full SWSS schema/safety validator. Its narrower input bound is a tool limit, not a new standard limit. Unit tests separately import this explicitly trusted fixture to exercise its real parser and numerical code. Discovery safety and execution testing are distinct.

The small [mutation cases](tests/fixtures/mismatches.json) create invalid metadata in memory for renamed flags, wrong types, aliases, defaults, choices, requiredness, actions, kind, malformed TOML and stale binding. Tests also alter source bytes to check stale hashes and omit required CLI values to exercise actual rejection. These mutations are not alternative companion files.

## Fault ownership

| Observation | First place to investigate |
| --- | --- |
| Analytic reference or timestep result is wrong | Simulation equation, implementation and numerical tests. |
| Parser differs from declarations | Simulation/TOML maintenance; run the contract checks. |
| Valid declarations or exact argv change during consumer editing | Consumer discovery/editor/persistence, with the exact declaration and token vector. |
| Independent implementations cannot resolve a requirement | A separate SWSS standards issue; do not silently reinterpret the contract. |
| Consumer-specific version, capture or UI behavior differs | That consumer's contracts and issue tracker. |

## Licensing

The Python source, author check, tests and JSON mutation fixtures in this directory are explicitly designated reference code under the existing [MIT code license](../../LICENSE-CODE), copyright (c) 2026 Johnny Mongstad. Prose and the illustrative `swss.toml` retain the repository's [documentation license](../../LICENSE.md). No license terms are changed.

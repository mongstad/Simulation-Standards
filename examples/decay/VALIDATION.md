# Reference validation evidence

Validation performed for issue #25 on 2026-10-20, on Linux with CPython 3.14.8. This report covers the initial `0.1.0` reference package and SWSS v2.0/schema 2. It is not independent scientific certification or a full consumer conformance report. Temporary run outputs are discarded by the reproducible tests; the assertions and fixtures are the retained evidence.

From the repository root:

```bash
python -B examples/decay/check_contract.py
python -B -m unittest discover -s examples/decay/tests -v
```

Observed: the contract check passed for all 12 declarations and the bound source digest; all 12 unit tests passed. No third-party packages are needed for these commands.

| Area | Expected and observed result | Limits |
| --- | --- | --- |
| Scientific baseline | Euler samples agree with the closed-form discrete recurrence; exact-step final concentration agrees with the continuous analytic solution to 14 decimal places for test inputs. | A scalar test problem, not an experimental validation; no GPU or parallel solver. |
| Instrumentation | Final diagnostic unchanged with series disabled and progress enabled; sample telemetry counts are 0, 5, 10, 15, 20 for the tested cadence. | No recorder metric integration or performance benchmark. |
| Provenance | Exact aliases, leading-zero integer spelling, exponent spelling, equals form, explicit empty string and omitted defaults remain distinct from resolved values; source digest and run IDs match. | Startup byte observation is not execution isolation; copied source/backup restoration is not tested by the core suite. |
| Outputs | Successive and simultaneous runs use separate roots; CSV numerical bytes match for identical inputs; prior artifact bytes remain unchanged. Forced root collision returns nonzero without overwrite. | Concurrent hostile filesystem modification and platform-specific filesystems are outside coverage. |
| Lifecycle | Injected arithmetic error records failure; injected interruption and real SIGTERM at a deterministic solver boundary record cancellation; partial CSV is retained. Injected summary-write failure returns nonzero without a completed log status. | SIGKILL/power loss can prevent finalization. Disk-full recovery and Windows signal behavior are untested. |
| Parser/metadata | All 12 rows agree with the actual argparse parser for aliases, kinds, types, actions, requiredness, choices and declared defaults. Required rate and context-dependent dt have no declared default. | `--help` is intentionally not a model parameter. The offline checker is specialized, not a general SWSS validator. |
| Negative cases | Eleven in-memory metadata mutations fail the contract check; changed source bytes fail binding; missing/invalid required values and choices fail argparse. | These are representative cases, not all §5.2 consumer cases or every resource-limit boundary. |
| Discovery separation | Static check accepts syntactically valid source containing an unexecuted top-level exception while execution, filesystem access, network and subprocess hooks are blocked. | Trusted unit tests separately execute the known fixture; arbitrary runtime discovery is not implemented. |

## SimShelf consumer check

The separate [API integration script](verify_simshelf.py) passed against SimShelf **0.1.0.40**, commit `c9589fb08d00cb49a70fcf16b437a48d73b1a58a`, with its existing development environment. SimShelf sources were read only. The script used a disposable copy of the simulation and a temporary library, with bytecode writes disabled. The sandboxed TestClient attempt stalled and was interrupted; a bounded unsandboxed rerun passed. The environment emitted a Starlette/httpx deprecation warning; no packages were changed.

To reproduce, select that consumer checkout and an already provisioned interpreter, set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH` to the consumer's `src` directory, and execute `examples/decay/verify_simshelf.py`. This optional command is separate from the dependency-free reference suite.

Expected and observed:

- Twelve supported rows; required `--rate`, unknown/context-dependent `--dt`, integer/float/string choices, known empty label, false `--progress` and true series defaults.
- Exact `['-k', '1e-1', '-n', '0010', '--label', '', '--no-series']` survives execution-settings save, application/store reopen and launch; omitted options remain omitted.
- Source binding reports `listed bytes verified`; the run retains exact `swss.toml` bytes and argv. The simulation writes resolved values separately.
- The run completes. Three artifacts (log, provenance, summary) are copied, and stored blob bytes match actual files.
- Malformed metadata, malformed binding and changed source disable typed rows with diagnostics. Explicit manual settings preserve argv. This does not bypass the simulation's argument checks.

Limitations requiring interpretation by the consumer owner:

- SimShelf's application-specific run version is `unversioned` because the application-independent fixture does not declare its local version tag. SWSS metadata and simulation provenance both retain `0.1.0`. This does not justify adding a mandatory consumer namespace to SWSS.
- The integration uses a fixed capture parent, not the coordinated-capture capability. Run directories remain isolated by the simulation; consumer-assigned output roots and full §3.1 behavior are not claimed.
- Verification exercises the API, persistence, recorder and artifact bytes. Browser parameter rendering, manual-editor interaction, frontend typed editing and UI save/reopen are untested. Expected row/default data is recorded above for that review.
- No consumer changes or consumer issues were created as part of this standards PR. Consumer-specific findings should be handled separately under that repository's workflow.

The normative specification, schema, license terms and external applications were not changed. The specification's existing statement that a first reference implementation is future work remains untouched because issue #25 explicitly excludes normative edits; this package is a scoped reference with the limits above.

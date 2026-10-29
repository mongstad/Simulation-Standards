# Reference validation evidence

## Current revision: 0.1.4 / SWSS v3.0 / schema 3

Validated 2026-10-29 on Linux, CPython 3.14.8, disposable local `tmpfs` paths. The reference is executable and supplies schema-3 author declarations; these observations are bounded evidence, not full baseline, consumer or platform certification.

From the repository root:

```bash
python -B examples/decay/check_contract.py
python -B -m unittest discover -s examples/decay/tests -v
python -B examples/decay-v2/check_contract.py
python -B -m unittest discover -s examples/decay-v2/tests -v
```

Both author checks pass for twelve parameter declarations and their respective source bindings. The current suite runs **59 tests: 53 pass, 6 explicitly skip**. The preserved legacy suite passes **14 tests**. All 41 [output-location case IDs](../../standards/SWSS/conformance/output-location.md) map to named tests in `tests/test_output_contract.py`; a passing function is not a claim that every observation in its written case was exercised.

| Cases | Executed observations and limits |
| --- | --- |
| S1–S10 | Root-level and nested entrypoints from a foreign working directory; explicit baseline root without a companion; successive/concurrent exclusive children; forced collision; internal/external parent overrides; retained source/input/lookalike sentinels; exact argv and stable numerical evidence. Concurrency is process allocation, not recorder attribution. External parents are sandbox directories, not separate volumes. |
| C4 | Standalone child allocation and explicit rejection of an unsupported root option without creating a destination. Legacy standalone behavior is tested separately. No parent-capture recorder or automatic capability detection is implemented. |
| C1–C3, C5–C6 | **Skipped:** no optional coordinated-root ownership/adapter or recorder. Direct-root agreement, coordinated conflicts/reuse, overlapping coordinated runs and capture budgets remain untested. Standalone collision/failure tests do not substitute for these cases. |
| N1–N3, N5–N9 | Unsafe paths, source/input overlap, symlink destinations/source aliases, literal runtime syntax, legacy schemas/extensions, stale/missing/unassociated declarations, preserved legacy working-directory behavior and immutable fixture history. Permission denial is injected in the retained regression suite, not tested with another OS user. Actual volume failure is not exercised. |
| N1b | **Skipped:** no required-mount identity contract or absent-mount test. No claim of removable/network-volume safety. |
| N4 | A controlled ancestor replacement is detected by the identity recheck helper. This does not test every allocation/snapshot interleaving or establish hostile-filesystem isolation; replacement windows remain between checks and operations. |
| M1–M7, M9 | Default/custom declarations, bound overrides and exact option forms; malformed paths/types/bindings, bounds, duplicate ownership and unresolved argv; unrelated scalar/flag controls. Custom-default behavior is tested in a disposable source variant with its parser default deliberately aligned. |
| M8, M15 | No inferred binding; an unbound declared control and a valid source-bound but behaviorally false declaration show why runtime comparison is required. A schema-number-only edit does not migrate a legacy script. There is no recorder to report capture outcomes. |
| M10 | Local destination conflict/lexical agreement. Filesystem alias validation is a separate launch check; no cached UI preview exists. |
| M11 | Fresh resolution after companion (including extension-only), argv, root, entrypoint, local destination and supplied source changes; stale and oversized binding refusal. This is stateless recomputation, not a tested consumer UI/persistence lifecycle. |
| M12–M13 | Explicit schema support, legacy reader rejection of schema 3, no invented schema-2 output default, future-version refusal, and pure discovery with writes/file access/process/network/exec operations forbidden by test hooks. |
| M14 | Effective external parent plus previously known default/custom internal parents remain excluded before reads; legitimate similarly named source remains eligible. Coordinated replacement-parent behavior is untested. |

Additional schema regressions cover unknown header fields, malformed shapes, duplicate keys, document/string limits, nonfinite metadata, manual-only unrelated rows, unsupported nested/date values, numeric grammar/type distinctions and source symlink/read-budget refusal. The retained lifecycle tests exercise computation failure, handled interruption, real SIGTERM and evidence-write failure while preserving partial evidence.

A before/after comparison against the byte-preserved 0.1.3 reference confirms identical ASTs for `resolve`, `advance`, `diagnostic` and `write_json`. Both revisions were run with `-k 1e-1 -n 0010 --dt=0.25 --label ''` under separate temporary parents, for Euler and exact-step methods: CSV bytes and final diagnostics match exactly. No scientific equation, numerical parameter semantics or RNG behavior changed.

All eight files in `examples/decay-v2/` are byte-identical to the previous `examples/decay/` tree at `16076539f33aa53a2392c2deeae2c3247aec58e8`. The complete v2.0 specification is also byte-preserved. Its schema-2 declarations and historical validation claims keep their original meaning. No historical run records, snapshots or Git history were rewritten.

### Harness boundaries

`output_contract.py` is a small reference harness, not a general production reader/editor, recorder or sandbox. Its **16 KiB metadata limit** is narrower than SWSS's 256 KiB limit. It uses the standard-library TOML parser with bounded input, then structural checks; it has no isolated parser resource worker and is not certified for adversarial parser-resource exhaustion. Source association bytes are supplied by the caller; `resolve_parent` does not safely discover arbitrary on-disk projects or stream those supplied bytes. The separate file helper bounds regular-file reads and compares identities. Hashing/fixture snapshots use 16 MiB per file and a 64 MiB aggregate budget; the runtime's explicit package manifest is small. These limits and caller responsibilities prevent a claim of complete metadata-consumer conformance.

The snapshot harness retains hashes in memory for comparison. It does not persist source bytes, enforce a production inclusion policy, discover historical output boundaries, or supply independent backup restoration. Callers explicitly supply required source/input paths and known generated parents. Unknown source/input roles cannot be inferred from file names. Check timing is observable, not process isolation. Real external mount loss, Windows/macOS paths, network filesystems, power loss/SIGKILL, disk-full recovery, backup restoration, live consumers and optional coordinated capture remain untested.

## Historical evidence: 0.1.3

The report below is retained verbatim from the preceding reference revision. Its commands, paths, scope and test counts describe that revision, not the current implementation; use `examples/decay-v2/` for its runnable preserved copy.

# Reference validation evidence

## Standalone revision: 0.1.3

Validated 2026-10-21 on Linux/CPython 3.14.8. Source and TOML version are **0.1.3**, with the refreshed entrypoint SHA-256 binding.

From the repository root:

```bash
python -B examples/decay/check_contract.py
python -B -m unittest discover -s examples/decay/tests -v
```

The author check passes for all twelve declarations and the source binding; all **14 tests pass**. No third-party packages are required. The checker remains a bounded, nonexecuting author tool specialized to this fixture, not a general SWSS validator.

| Coverage | Observed result |
| --- | --- |
| Output allocation | Default `outputs`, nested custom parents, both explicit option forms, repeated runs and simultaneous processes create distinct exclusive run directories. Prior file bytes remain unchanged. Forced root collision fails without overwrite or fallback allocation. |
| Allocation errors | A file at the parent or in its ancestry fails without changing existing evidence. Injected permission failure returns nonzero with a diagnostic. |
| Evidence and lifecycle | Exact argv, resolved values, source hashes, run identity, effective output directory and timestamped logs are retained. Computation failure, handled interruption and real SIGTERM preserve partial evidence. Retrying uses a fresh directory; prior failed-run bytes remain unchanged. Summary-write failure cannot report completed log status. |
| Science | Euler samples match the discrete recurrence; exact-step results match the analytic solution to 14 decimal places. Instrumentation and output-parent choices preserve final diagnostics. |
| Metadata | All twelve declarations agree with the actual parser. Eleven negative metadata mutations and changed source bytes are rejected; invalid/missing CLI values fail. Static checking does not execute source or perform network, subprocess or write operations. |

A separate before/after comparison against commit `457b5c5f3d8bec26535173e716ced94986d4140a` verified unchanged ASTs for the parser, parameter resolution, numerical step, diagnostics, JSON writer and main function, plus unchanged parameter declarations. Running both revisions with `-k 1e-1 -n 0010 --dt=0.25 --label ''` for each of `--method euler` and `--method exact` under separate temporary output parents produced identical CSV bytes and final diagnostics.

The simulation now always allocates its own root. Adapter-only claims and allocation-mode fields are removed; effective output paths remain in logs, provenance and summaries. No replacement environment transport is defined. This example does **not** implement optional SWSS §3.1 coordinated capture. Portable metadata and the illustrative progress emitter retain their documented scope in the [README](README.md).

The reference subtree audit found no remaining named-consumer paths or content. Six relative documentation links/anchors, Python syntax and whitespace checks passed. Changes are confined to this reference subtree; normative requirements and license terms are unchanged.

## Limits and historical evidence

These are reference behavior checks, not full baseline or consumer certification. Backup restoration, hostile filesystem replacement, power loss/SIGKILL, disk-full recovery, other operating systems and recorder behavior are untested. Parent paths follow normal filesystem resolution; no sandbox or symlink-containment guarantee is made. Permission failure is injected, not an operating-system access-control test. Startup hashes observe bytes, not process isolation.

Earlier 0.1.0–0.1.2 validation reports and removed integration coverage remain in Git history at `457b5c5f3d8bec26535173e716ced94986d4140a`, under their original paths. For example, `git show 457b5c5f3d8bec26535173e716ced94986d4140a:examples/decay/VALIDATION.md` retrieves the prior report. Those reports describe earlier revisions and are not current execution instructions. No historical run records or Git history were changed.

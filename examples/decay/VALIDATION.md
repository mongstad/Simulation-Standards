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

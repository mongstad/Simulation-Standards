# Simulation Standards

**Reproducible experiments. Predictable outputs. Independent tools.**

This repository documents the voluntary **Scientific Workflow Simulation Standard (SWSS)** for Python scientific simulations.

**Status:** SWSS v1.0 is a draft for owner review, not a ratified or independently certified standard.

- [Read the single authoritative SWSS v1.0 draft](standards/SWSS/v1.0.md)
- [Review and validation gates](docs/REVIEW.md)
- [Draft consolidation decisions and contract review](docs/SWSS_V1_RECONCILIATION.md)
- [Publication readiness, audit findings and proposed licensing](docs/PUBLICATION_READINESS.md)

## Modular adoption

| Profile | Goal | Software required |
| --- | --- | --- |
| Core | Scientific versions, reproducibility, logs and lifecycle | Neither application |
| SimShelf | Optional run recording, progress, metrics and automatic file capture | SimShelf |
| Wavez | Optional WVZ1 export and validation | Wavez |
| Full | Core plus both integrations | Both |

Wavez and SimShelf are independent software products. Their APIs and file contracts are authoritative in their respective repositories. SWSS does not prescribe dependencies for either application.

Existing scientific simulations need not be migrated until they are selected for future work. Scientific results must not be silently altered merely to meet workflow conventions.

## Pilot evidence and validation status

[Issue #6](https://github.com/mongstad/Simulation-Standards/issues/6) reports a workflow observation from VB Vacuum Collapse Recirculator v0.4.3: the default `case_D.wvz` name could collide on a repeated run. This informed the draft's unique-capture naming rules; it is not evidence of scientific correctness, full compatibility or SWSS conformance. No pilot artifacts or completed conformance report are tracked here.

The [review gates](docs/REVIEW.md) still require scientific baseline comparisons, automatic log capture, progress/metric checks, failure/cancellation, WVZ1 readback/viewer checks, repeated-run collision tests and backup evidence. The synthetic reference implementation remains future work. No implementation is certified by this repository.

**Publication:** The repository remains private during the readiness review. Publication requires a separate owner decision after reviewing the [audit and blockers](docs/PUBLICATION_READINESS.md).

**Governance:** Owner-directed review and publication. Public readability does not imply open contribution intake.

**Licensing:** No repository license has been approved. CC BY 4.0 for documentation and MIT for future reference code are proposals only; exact scope, attribution and embedded-example treatment await owner approval. See the [licensing proposal](docs/PUBLICATION_READINESS.md#licensing-proposal--no-grant-made).

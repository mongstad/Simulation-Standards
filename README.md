# Simulation Standards

**Reproducible experiments. Predictable outputs. Independent tools.**

This repository documents the voluntary **Scientific Workflow Simulation Standard (SWSS)** for Python scientific simulations.

**Status:** SWSS v1.0 is a draft for owner review, not a ratified or independently certified standard.

- [Read the single authoritative SWSS v1.0 draft](standards/SWSS/v1.0.md)
- [Review and validation gates](docs/REVIEW.md)
- [Draft consolidation decisions and contract review](docs/SWSS_V1_RECONCILIATION.md)

## Modular adoption

| Profile | Goal | Software required |
| --- | --- | --- |
| Core | Scientific versions, reproducibility, logs and lifecycle | Neither application |
| SimShelf | Optional run recording, progress, metrics and automatic file capture | SimShelf |
| Wavez | Optional WVZ1 export and validation | Wavez |
| Full | Core plus both integrations | Both |

Wavez and SimShelf are independent software products. Their APIs and file contracts are authoritative in their respective repositories. SWSS does not prescribe dependencies for either application.

Existing scientific simulations need not be migrated until they are selected for future work. Scientific results must not be silently altered merely to meet workflow conventions.

**Governance:** Owner-directed review and publication. Public readability does not imply open contribution intake.

**Licensing:** A repository license has not been selected yet; documentation/code reuse permissions must be determined before public publication.

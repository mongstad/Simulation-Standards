# Simulation Standards

Simulation Standards documents the **Scientific Workflow Simulation Standard (SWSS)**, a voluntary workflow convention for people writing and maintaining Python scientific simulations.

SWSS helps make experiments easier to reproduce and review through source versioning, predictable output directories, logs and provenance—the record of how a result was produced. It also defines optional integrations for recording runs and visualizing simulation data, while keeping the numerical model authoritative.

**Status:** SWSS v1.0 is a **Draft** for owner review, not a ratified industry standard or certification of an implementation.

## Choose a profile

| Profile | What it covers | Software required |
| --- | --- | --- |
| **Core** | Versioning, reproducibility, logs, provenance and truthful run status | Neither application |
| **SimShelf** | Core plus run recording, progress, metrics and automatic file capture with SimShelf | SimShelf |
| **Wavez** | Core plus WVZ1 simulation recordings and validation for the Wavez viewer | Wavez |
| **Full** | Core plus both integrations | SimShelf and Wavez |

SimShelf organizes simulation runs and their evidence; Wavez visualizes exported simulation data. They are independent applications: adopting either integration does not require the other. Each application's own documentation governs its APIs and file formats.

## Get started

1. Read the [authoritative SWSS v1.0 draft](standards/SWSS/v1.0.md) and choose the profile that fits your workflow.
2. Apply the relevant requirements to a new simulation or one selected for future work. Document parameters, source identity and outputs without silently changing scientific behavior.
3. Use the [review and validation gates](docs/REVIEW.md) to check the profiles you claim and record any deviations or untested behavior.

Existing simulations can be adopted one at a time; no mass migration is required. Application integration references are collected in the [specification](standards/SWSS/v1.0.md#6-authoritative-references).

## Licensing and governance

Original specification, documentation and embedded examples are licensed under [CC BY 4.0](LICENSE.md). Future standalone executable reference code is covered by [MIT](LICENSE-CODE) only when explicitly designated and marked as such. SimShelf and Wavez retain their own licenses.

Development and publication are owner-directed. Public readability does not imply open contribution intake.

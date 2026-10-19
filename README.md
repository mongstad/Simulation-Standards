# Simulation Standards

Simulation Standards defines the **Scientific Workflow Simulation Standard (SWSS)**, an independent, voluntary standard for scientific simulation workflows.

SWSS supports reproducible experiments through source versioning, exact arguments, isolated outputs, logs, provenance and truthful run status. Simulations remain independently executable and authoritative for their scientific behavior. Developers are free to adopt or ignore the standard.

## Baseline and optional capabilities

The baseline protects scientific integrity. Independent optional capabilities cover coordinated run capture, progress and metrics, scientific exports, and portable parameter editing. No particular application, library or binary format is required.

Participating configurations use one `swss.toml`: portable metadata and optional parameter declarations live under `swss`; bounded optional extension data cannot override that contract.

## Get started

1. Read the [SWSS v2.0 specification](standards/SWSS/v2.0.md) and identify the baseline and optional capabilities you intend to claim.
2. Apply and validate those requirements for a simulation selected for future work, preserving scientific behavior and historical evidence.

v2.0 replaces the earlier profile taxonomy and uses portable schema 2. Its text is submitted for owner review; no release, ratification, external implementation or scientific certification is claimed. Portable additions are specified here first, then implemented by adopting tools.

## Licensing and governance

Original specification, documentation and embedded examples are licensed under [CC BY 4.0](LICENSE.md). Future standalone executable reference code is covered by [MIT](LICENSE-CODE) only when explicitly designated and marked as such. Third-party material retains its own licenses.

Development and publication are owner-directed. Public readability does not imply open contribution intake.

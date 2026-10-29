# Simulation Standards

Simulation Standards defines the **Scientific Workflow Simulation Standard (SWSS)**, an independent standard for scientific simulation workflows.

SWSS supports scientific integrity, reproducibility and portability through source versioning, exact arguments, isolated outputs, logs, provenance and truthful run status. Simulations remain independently executable and authoritative for their scientific behavior. Consuming applications implement the standard without defining its requirements.

## Baseline and optional capabilities

SWSS v3.0 is the current specification. Its baseline protects scientific integrity. Independent optional capabilities cover coordinated run capture, progress and metrics, scientific exports, and portable configuration and parameter editing. No particular application, library or binary format is required.

The portable configuration capability uses schema 3 in one `swss.toml` file.

## Get started

Read the [SWSS v3.0 specification](standards/SWSS/v3.0.md) for requirements and validation criteria, then identify the baseline and optional capabilities relevant to your simulation or tool.

Try the [scalar decay reference simulation](examples/decay/README.md) for a small executable example and contract checks.

The [v2.0 specification](standards/SWSS/v2.0.md) and byte-preserved [schema-2 reference](examples/decay-v2/README.md) remain available for historical/compatible workflows. They retain their original semantics; no automatic migration is performed. See [adoption and reader compatibility](standards/SWSS/v3.0.md#6-adoption-and-reader-compatibility) and [output-location cases](standards/SWSS/conformance/output-location.md).

## Licensing and governance

Original specification, documentation and embedded examples are licensed under [CC BY 4.0](LICENSE.md). Future standalone executable reference code is covered by [MIT](LICENSE-CODE) only when explicitly designated and marked as such. Third-party material retains its own licenses.

Development and publication are owner-directed. Public readability does not imply open contribution intake.

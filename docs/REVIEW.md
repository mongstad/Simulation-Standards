# SWSS v1.1 implementation review gates

**Specification versus implementation:** The [normative SWSS v1.1 specification](../standards/SWSS/v1.1.md) defines the contract. These gates collect implementation evidence; they do not reopen specification design or authorize application edits, merge, release or settings changes. [v1.0](../standards/SWSS/v1.0.md), the [parameter proposal](proposals/0016-parameter-metadata.md) and the [consolidation review](SWSS_V1_RECONCILIATION.md) are historical records, not competing current specifications.

Apply integration gates only to profiles being claimed; Full requires both. Record tested tool versions, deviations and untested paths. These gates remain open until evidence is supplied.

- [ ] Record the claimed v1.1 profiles and applicable optional parameter capability; verify their independent boundaries.
- [ ] Core: validate source-package version bump rules and document whether the project version gate warns or blocks a run; stale metadata must disable typed use as specified; distinguish labels, exact source and structural fingerprints.
- [ ] Core: verify unique timestamped logs/paths, resolved parameters and provenance, diagnostic formulas/units/timestamps, and scientific baseline before/after instrumentation.
- [ ] Core: test success, intentional failure and handled cancellation; check exit status, file closure, partial evidence and restart lineage where applicable.
- [ ] SimShelf adoption: verify the complete reader/launch/capture/discovery path uses `swss.toml` and `[apps.simshelf]` before retiring the old reader; no partially converted release or legacy compatibility machinery. This application work is separately authorized.
- [ ] Optional parameter capability: execute the [conformance cases](../standards/SWSS/v1.1.md#67-conformance-cases), including absent parameters, exact argv, bounded data-only parsing, stale/unsafe inputs, namespace isolation and preservation of historical run evidence.
- [ ] SimShelf: verify registration and controls against actual accepted arguments and runtime defaults; preserve the explicit revision label and compare it with `swss.simulation_version`.
- [ ] SimShelf: verify output-directory resolution with launcher and joined API, including explicit `--output` and two simultaneous runs with distinct capture targets.
- [ ] SimShelf: show automatic timestamped `.log` capture into Files from `output/logs/` using an ordered copy rule and realistic size budgets: **zero manual uploads**. Inspect missing/skipped/oversized artifacts and capture status separately from solver status.
- [ ] SimShelf: test native stdout/stderr Logs and supported step/structured progress with the required adapter/library configuration and compatibility preparation.
- [ ] SimShelf: verify real metric entries against independently calculated solver diagnostics, including timestamps, definitions, units and nonfinite handling; inspect independent JSON/CSV evidence.
- [ ] Wavez: generate WVZ1 with SceneCapture, read actual payloads via matching SceneReader and compare values/dtypes, geometry, timestamps, units, channels and applicable identity history; inspect a representative file in Wavez.
- [ ] Wavez: run two consecutive captures with identical scientific parameters and default destination selection; verify distinct full paths, separately readable SceneReader payloads, and unchanged first-artifact bytes. Check the recommended descriptive timestamped names (or documented per-run-directory identity) and matching run IDs in captures, logs and metadata/diagnostic manifests.
- [ ] Wavez: request an existing explicit `--wavez-file` destination (or equivalent); verify clear collision refusal, unchanged existing bytes, and no silently renamed output without documented opt-in. Distinguish collision errors from other filesystem failures; unique names do not guarantee I/O success.
- [ ] Wavez: compare export enabled/disabled numerical state and RNG behavior; test export failure/partial-file handling and preserve independent scientific archives according to the documented policy.
- [ ] Core and applicable integrations: verify independent backups of source and large referenced artifacts; reference-only records are not backups.
- [ ] Review [publication-readiness findings](PUBLICATION_READINESS.md), verify the approved [documentation license](../LICENSE.md) and [MIT code license](../LICENSE-CODE), and review identifying history and remaining hosted surfaces before any separately authorized public-visibility change.
- [ ] After successful reference test, owner reviews and authorizes any tag/publication.

**Planned reference pilot:** One copied synthetic scalar simulation, kept separate from either application's required source tree. Keep both applications independent. Migrate historical sims only if and when selected for future runs. No pilot execution or migration is part of issue #1.

The external pilot observation reported in [issue #6](https://github.com/mongstad/Simulation-Standards/issues/6) is described in the [readiness report](PUBLICATION_READINESS.md); it does not complete these gates. Issue #8 performs documentation/audit work only.

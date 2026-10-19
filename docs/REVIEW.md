# SWSS v2.0 implementation review checklist

The [specification](../standards/SWSS/v2.0.md) defines the baseline and independent optional capabilities. These unchecked gates require implementation evidence; they are not claims of completed tests or authority to edit external repositories. Earlier tracked documents are archival summaries, not competing contracts.

- [ ] Identify revision, simulation/tool versions, claimed capabilities, environment, expected/observed results, deviations and untested paths.
- [ ] Baseline: check version bumps, exact source identity and argv, resolved parameters, scientific baseline/RNG behavior, units, diagnostic formulas and sampled timestamps.
- [ ] Baseline: exercise success, intentional failure, handled cancellation and concurrent runs; verify isolated outputs, unchanged previous artifacts, timestamped logs and truthful partial evidence.
- [ ] Coordinated capture, if claimed: verify agreed output roots and conflicting arguments, automatic log copy with no manual upload, process streams, capture limits, missing/skipped artifacts, snapshot exclusions and independent backups.
- [ ] Progress/metrics, if claimed: check finite and indeterminate reporting, real versus synthesized progress, nonfinite/dropped values, retention and independently calculated measurements.
- [ ] Scientific export, if claimed: validate format/version and actual payload readback against source; check dtype, geometry, channels, units, timestamps, identities, collisions, I/O failure and representative visualization where applicable.
- [ ] Portable configuration, if claimed: execute every [metadata case](../standards/SWSS/v2.0.md#52-portable-metadata-cases), including absent rows, schema rejection, extensions, safety limits, exact argv, stale binding and manual fallback.
- [ ] Adoption: validate all affected paths before retiring prior readers; verify historical records, snapshots, argv, artifacts and provenance unchanged. Do not release a partially converted consumer.
- [ ] Documentation: scan every tracked path/content including hidden files for forbidden product references, validate links/anchors and TOML examples, review compatibility/status labels and preserve legal notices.
- [ ] Before separately authorized publication: review [historical readiness findings](PUBLICATION_READINESS.md), current hosted surfaces, attribution, [documentation license](../LICENSE.md) and [code license](../LICENSE-CODE).

No runtime gate is completed by editing documentation. Owner authorization remains required for merge, release, tags, settings or publication; no consumer or scientific certification follows from specification acceptance.

# SWSS v1.0 review gates

**Draft status:** No application modifications, merge, tag or public release is approved by this checklist. The [single specification](../standards/SWSS/v1.0.md) defines requirements; the [consolidation review](SWSS_V1_RECONCILIATION.md) records documentation decisions, not runtime validation.

Apply integration gates only to profiles being claimed; Full requires both. Record tested tool versions, deviations and untested paths. These gates remain open until evidence is supplied.

- [ ] Owner approves the Core / SimShelf / Wavez / Full profile boundaries and naming.
- [ ] Core: validate source-package version bump rules and decide whether version mismatch warns or blocks a run; distinguish labels, exact source and structural fingerprints.
- [ ] Core: verify unique timestamped logs/paths, resolved parameters and provenance, diagnostic formulas/units/timestamps, and scientific baseline before/after instrumentation.
- [ ] Core: test success, intentional failure and handled cancellation; check exit status, file closure, partial evidence and restart lineage where applicable.
- [ ] SimShelf: verify registration and discovered/schema controls against actual accepted arguments and runtime defaults.
- [ ] SimShelf: verify output-directory resolution with launcher and joined API, including explicit `--output` and two simultaneous runs with distinct capture targets.
- [ ] SimShelf: show automatic timestamped `.log` capture into Files from `output/logs/` using an ordered copy rule and realistic size budgets: **zero manual uploads**. Inspect missing/skipped/oversized artifacts and capture status separately from solver status.
- [ ] SimShelf: test native stdout/stderr Logs and supported step/structured progress with the required adapter/library configuration and compatibility preparation.
- [ ] SimShelf: verify real metric entries against independently calculated solver diagnostics, including timestamps, definitions, units and nonfinite handling; inspect independent JSON/CSV evidence.
- [ ] Wavez: generate WVZ1 with SceneCapture, read actual payloads via matching SceneReader and compare values/dtypes, geometry, timestamps, units, channels and applicable identity history; inspect a representative file in Wavez.
- [ ] Wavez: compare export enabled/disabled numerical state and RNG behavior; test export failure/partial-file handling and preserve independent scientific archives according to the documented policy.
- [ ] Core and applicable integrations: verify independent backups of source and large referenced artifacts; reference-only records are not backups.
- [ ] Choose documentation and reference code licenses before going public.
- [ ] After successful reference test, owner reviews and authorizes v1.0 tag/publication.

**Pilot:** One copied synthetic scalar simulation, kept separate from either application's required source tree. Keep both applications independent. Migrate historical sims only if and when selected for future runs. No pilot execution or migration is part of issue #1.

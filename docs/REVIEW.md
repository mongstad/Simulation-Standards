# SWSS v1.0 review gates

**Draft status:** No application modifications, merge, tag or public release is approved by this checklist.

- [ ] Owner approves the Core / SimShelf / Wavez profile boundaries and naming.
- [ ] Validate version bump rules and decide whether version mismatch blocks a run.
- [ ] Verify output-directory resolution with SimShelf's actual launcher and joined API, including any explicit --output.
- [ ] Show automatic .log capture into Files from output/logs/ using a copy rule and realistic size budgets: **zero manual uploads**.
- [ ] Test native stdout Logs and supported step/structured progress with the required adapter/library configuration.
- [ ] Verify real metric entries correspond to source solver state, with correct timestamps, definitions and units.
- [ ] Generate WVZ1 with SceneCapture, verify readback via SceneReader and inspect it in Wavez.
- [ ] Test successful and intentional failed/interrupted runs; ensure partial files are identified truthfully.
- [ ] Preserve scientific baseline and independent external backup strategy.
- [ ] Choose documentation and reference code licenses before going public.
- [ ] After successful reference test, owner reviews and authorizes v1.0 tag/publication.

**Pilot:** One copied synthetic scalar simulation, kept separate from either application's required source tree. Keep both applications independent. Migrate historical sims only if and when rerun.

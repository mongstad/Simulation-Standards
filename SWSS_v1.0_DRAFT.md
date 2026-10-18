# SimShelf–Wavez Simulation Standard (SWSS) v1.0

**Status:** Draft for owner review — 2026-10-18  
**Scope:** New Python scientific simulations and existing simulations when intentionally updated or rerun.  
**Maintainer:** SimShelf / Wavez project owner.  
**Normative terms:** **MUST** = required for SWSS conformance; **SHOULD** = recommended, with documented exceptions; **MAY** = optional.

## 1. Purpose and governing principles

A SWSS-compliant simulation can be registered, parameterized, executed, monitored and reviewed through SimShelf, and can produce scientifically faithful recordings compatible with the current supported Wavez reader. Reproducibility, scientific integrity and predictable output handling take precedence over convenience.

- The simulation and numerical solver remain authoritative for science; SimShelf records and organizes runs; Wavez visualizes exported arrays.
- The standard does **not** require changing the model's equations, timestep, grid, random streams or numerical precision merely for integration.
- Scientific data, SimShelf metric values and Wavez colors/visualization are distinct. Do not infer scientifically measured values from rendered pixels.
- Never silently overwrite completed runs, checkpoints or `.wvz` captures.
- Existing simulations are migrated **only when selected for future work**; no mass conversion is required.

## 2. Compatibility baseline

### SimShelf

- MUST register with a stable main Python entry point and a `simshelf.toml` configuration matching the application's current schema.
- MUST use the currently supported SimShelf version tag, for example `SIMSHELF_VERSION = "0.1.0"` as a literal in the registered version file. `simshelf.toml`'s `version_file` must point to that file.
- MUST define user-adjustable experiment parameters using statically discoverable `argparse` declarations whenever possible. If the parser is dynamic or unsupported, MAY declare a verified `simshelf-arguments.json` schema in the source root.
- MUST correctly honor the effective run output location (in priority order: the active SimShelf Python run context's `run.output_dir` or `SIMSHELF_OUTPUT_DIR` for a SimShelf-launched run; explicitly specified `--output` where applicable; otherwise a unique standalone output folder). The exact priority for overlapping explicit settings MUST be documented and tested; never write to two conflicting run destinations.
- MUST terminate with exit status zero only on success and nonzero on unrecovered failure. Preserve tracebacks and incomplete-run evidence.

### Wavez

- MUST use the supported WVZ1 `.wvz` capture format and the installed `wavez_export.SceneCapture` writer API, rather than an obsolete SSC/SIMSCP4 or custom binary visualization format.
- MUST obey the currently checked-out Wavez `WAVEZ_API.md`, `docs/WVZ1_FORMAT.md`, `docs/CAPTURE_FORMAT_POLICY.md` and `docs/SIMULATION_INTEGRATION_GUIDE.md`. The current writer/reader contract is authoritative over this summary.
- MUST export actual solver timestamps and explicitly defined world-coordinate geometry and units. Volume arrays use `(nz,ny,nx)` with xyz origin and spacing; particle and mesh geometry and stable identifiers must respect API rules.
- MUST validate each requested `.wvz` artifact using the matching SceneReader and SHOULD test it in the current Wavez viewer on a small sample.
- MAY offer a `--wavez` / `--no-wavez` control to avoid costly captures; a simulation claiming full SWSS-Wavez conformance MUST supply and test a Wavez export path. For extremely large jobs, output cadence and data volume SHOULD be configurable independently of solver cadence.

## 3. Scientific version and source identity

- `SIMSHELF_VERSION` is the **authoritative human-assigned SWSS simulation revision label**, distinct from SimShelf application build numbers and Wavez file format versions.
- For SWSS-managed source, **every accepted modification to the simulation source package** (including logging, progress and export behavior) MUST increment the version before the next recorded run. A simple policy is `MAJOR.MINOR.PATCH`: breaking model changes = major; significant scientific/algorithm revisions = minor; corrections/instrumentation/housekeeping = patch. The scheme is a house rule, not an existing SimShelf auto-bump feature.
- Runtime parameter changes alone do not bump source version: they create separate run records.
- SimShelf's **exact captured source snapshot and structural fingerprint remain independent evidence**. Matching version labels alone never prove identical code; a fingerprint is not proof of identical behavior.
- SHOULD add a pre-run conformance check which identifies source changes under an unchanged version relative to the preceding SWSS run. Initially this is a **warning/blocking policy in the development workflow**, not a claimed built-in SimShelf safeguard. If implemented inside SimShelf, the app MUST not auto-edit research source files.

## 4. Progress and measurements

### Progress

- MUST report progress by default during finite jobs, unless progress is intrinsically indeterminate (in which case report truthful stage descriptions and avoid a fake percentage).
- Preferred: SimShelf structured `run.progress(current=..., total=..., stage=...)` with explicitly enabled compatible library and installed SimShelf Python package in the selected interpreter.
- Portable fallback: print dedicated clean stdout lines such as `Step 1000 of 50000` with `flush=True`. Configure SimShelf's **Step counts** adapter for that launch; the adapter is currently **opt-in** and must not be assumed to auto-detect arbitrary text.
- MUST not mix progress counts and scientific time; a full progress bar does not certify successful execution.
- SHOULD rate-limit updates to avoid scientific slowdown and logging bloat. No per-cell/per-particle printing.

### Measurements

- SHOULD define at least one physically meaningful numeric diagnostic, where appropriate, through `run.metric(name, value, step=..., sim_time=...)` in a joined SimShelf run. A model without meaningful diagnostics MUST document why.
- MUST name metrics consistently, define units and formulas in README, and use valid finite values or explicitly handle nonfinite outcomes without disguising errors.
- SHOULD export the same diagnostics to `measurements.csv` (complete time series) and `summary.json` (summary and provenance) under the run output directory for independent inspection. SimShelf's latest-measurement panel is only a summary view.
- MUST compute metrics from numerical solver state, not colormap output or a Wavez viewport screenshot.
- MUST make metric timestamps correspond to the actual solver state sampled; distinguish sampled values, derived estimates and visual interpolation.

## 5. Logs and automatic SimShelf capture (NO manual uploads)

### Required behavior

Every run MUST write a timestamped, uniquely identifiable human-readable log and MUST expose it in that run's **SimShelf Files** record automatically when launched through SimShelf. Native SimShelf stdout/stderr run logs MUST also remain available in its **Logs** tab. There is no mandatory post-run import, manual upload, or manual copying by the owner.

### Portable v1.0 design, requiring no new SimShelf feature

1. The script creates a local convenience mirror beside the registered entry file, inside `logs/` (e.g., `logs/scalar_field_20261018T123000Z_v0.1.1_ab12cd.log`).
2. **At the same time**, the script writes an independent copy using a second logging handler to `<effective_run_output_dir>/logs/<same_filename>`. This is a real file, **not** a symlink. Each run has a unique output folder.
3. `simshelf.toml` capture policy MUST include `**/*.log` under the declared output directory, normally `copy`, with reasonable limits. Thus SimShelf automatically discovers the run-specific output copy on final capture. Run files are scoped by the output folder, not by scanning arbitrary folders next to the source file.
4. Handlers are flushed and closed during normal shutdown, errors and handled interruption. Failure paths preserve evidence as far as possible; a force-kill may leave partial files.
5. To avoid uncontrolled disk growth, local mirrors SHOULD have a documented rotation/retention policy, **never deleting logs needed by active runs**. SimShelf's retained copies and backups have their own retention policy.

**Why dual-write?** SimShelf's current final file capture scans its configured output folder for new/changed files; it does **not** promise to auto-ingest files written arbitrarily beside `simulate.py`. Directing one logging handler into the active output folder achieves automatic capture with existing functionality. A future SimShelf enhancement MAY provide first-class external-log registration, but SWSS v1.0 MUST NOT depend on that feature.

Capture policy MUST explicitly report oversized/skipped logs as incomplete capture; a completed solver does not guarantee every output was retained. The actual matched rule, per-file size limit and total copy budget MUST be tested. Do not rely on a change to a capture rule retroactively applying to previous runs.

## 6. Output organization and naming

Suggested source layout:

```text
scalar_field/
  simulate.py
  simshelf.toml
  README.md
  requirements.txt
  logs/
    scalar_field_20261018T123000Z_v0.1.1_ab12cd.log   # local convenience mirror
  outputs/
    run_20261018T123000Z_ab12cd/
      logs/
        scalar_field_20261018T123000Z_v0.1.1_ab12cd.log # auto-captured
      scene.wvz
      summary.json
      measurements.csv
      checkpoint.npz                                  # optional
```

- `ab12cd` is illustrative: use a collision-resistant run suffix or unique run ID, not an assumed six-character universal identifier.
- Timestamps SHOULD be UTC ISO-8601 basic form (`YYYYMMDDTHHMMSSZ`). File timestamps do **not** replace actual solver simulation time.
- Each run MUST have an isolated output directory; concurrent runs MUST NOT share overlapping SimShelf capture folders.
- Names MUST be deterministic in type/purpose and unique in run identity; never replace existing results silently.
- Raw large `.wvz`, binary grids and checkpoints SHOULD normally use **reference** capture rules with explicit external backups. Small text JSON/CSV/log and preview images SHOULD normally use **copy**. Exact limits are project dependent.
- `outputs/`, `logs/`, build environments, temporary files and large scientific artifacts SHOULD be excluded from source snapshots/archive rules where appropriate; archived research **source and small text evidence** should remain included.

## 7. Provenance and reproducibility

Per run, MUST record: simulation name and scientific version, time started, actual CLI arguments/resolved parameters, numerical timestep/solver configuration, output sample cadence, model/grid extent and units, selected Python version, and random seed/state policy where applicable. SHOULD record dependency versions, GPU/backend/precision, numerical assumptions, source snapshot identity, relevant input hashes, and checkpoint lineage. Never put credentials or private tokens in logs or metadata.

A `summary.json` MUST distinguish quantities that are physically modeled from purely diagnostic or dimensionless values. Exact run reproduction may still be limited by floating-point backends, parallel scheduling, library versions and external inputs: disclose those limits.

## 8. Interruption, failure, performance and lifecycle

- MUST not mark an incomplete capture as complete or label a failed run successful.
- MUST cleanly close Wavez writers, text logs and measurements on normal completion; failures SHOULD preserve partial evidence, but a partial `.wvz` MUST NOT be represented as a verified complete artifact.
- SHOULD honor normal interruption/cancellation signals and record reason where safely possible.
- MUST keep output/export cadence separate from integration timestep and avoid changes to scientific RNG state merely for exporting.
- MAY implement restart checkpoints; `.wvz` is **not** a solver restart/checkpoint format.
- MUST not place large binary outputs into Git history by default; use SimShelf references and separate data backups.

## 9. Acceptance checklist for each new or migrated simulation

- [ ] Simulation's equations/results match a pre-integration baseline or the scientific differences are explicitly approved and documented.
- [ ] SimShelf successfully registers the entry point and discovers declared controls (or provides a validated explicit schema).
- [ ] `SIMSHELF_VERSION` is present; changes since the last accepted revision carry a new version.
- [ ] Effective output folder matches both the simulation and SimShelf's capture target, including when two runs execute concurrently.
- [ ] A normal finite run shows live progress with supported structured API or selected stdout adapter.
- [ ] Scientific metrics appear in SimShelf, when applicable, and match independently calculated reference quantities.
- [ ] Native stdout/stderr appears in Logs; timestamped `.log` appears **automatically in Files without manual upload**.
- [ ] Required JSON/CSV/preview artifacts are captured; copy/reference rules and size limits have been examined.
- [ ] A short WVZ1 output passes matching SceneReader validation, including timestamps, units, object/channel shape and array readback; it opens in Wavez.
- [ ] Failed and cancelled smoke tests give truthful exit status and preserve available partial evidence.
- [ ] Run records contain the actual source/version, parameters and provenance, with clear limitations.
- [ ] Large artifacts and source files have an independently verified backup strategy.

## 10. Adoption plan and out-of-scope work

1. Review this draft against current SimShelf and Wavez code/contracts. Freeze v1.0 only after agreement on log capture, version enforcement and metrics.
2. Adapt **one small reference simulation**; test both normal completion and a deliberate failure in SimShelf and the generated file in Wavez.
3. Publish a reusable Python starter template or helper library only if it decreases boilerplate without coupling numerical code to SimShelf internals.
4. Apply to old simulations **one at a time, when chosen for future reruns**. Do not rewrite or mass-migrate historical data.

**Not required for SWSS v1.0:** automatic SimShelf detection of arbitrary external log paths; an automatic source-version bump by SimShelf; embedding `.wvz` inside the SimShelf database; auto-uploading outputs to cloud storage; using Wavez video exports as scientific ground truth; scientific solver restart from WVZ1.

## 11. Contract references (checked 2026-10-18)

- [SimShelf README](https://github.com/mongstad/SimShelf/blob/main/README.md)
- [SimShelf preserved data / versions / capture](https://github.com/mongstad/SimShelf/blob/main/docs/DATA.md)
- [SimShelf progress adapters and structured API](https://github.com/mongstad/SimShelf/blob/main/docs/PROGRESS.md)
- [SimShelf parameter discovery](https://github.com/mongstad/SimShelf/blob/main/docs/PARAMETER_DISCOVERY.md)
- [SimShelf sample script](https://github.com/mongstad/SimShelf/blob/main/examples/scalar_field/simulate.py)
- [SimShelf sample capture configuration](https://github.com/mongstad/SimShelf/blob/main/examples/scalar_field/simshelf.toml)
- [Wavez getting started / integration](https://github.com/mongstad/Wavez/blob/main/GETTING_STARTED.md)
- [Wavez Python API](https://github.com/mongstad/Wavez/blob/main/WAVEZ_API.md)
- [Wavez wire format](https://github.com/mongstad/Wavez/blob/main/docs/WVZ1_FORMAT.md)

This document is a **proposed cross-project house standard**, not a claim that all these rules are automatically enforced by either app today.

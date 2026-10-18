# SWSS v1.0 consolidation review

This is the documentation review for [issue #1](https://github.com/mongstad/Simulation-Standards/issues/1), not a second specification or evidence of a tested simulation. The single authoritative **draft** is [SWSS v1.0](../standards/SWSS/v1.0.md).

## Sources and scope

Compared the [original detailed draft](https://github.com/mongstad/Simulation-Standards/blob/8f818b7/SWSS_v1.0_DRAFT.md) and [modular draft](https://github.com/mongstad/Simulation-Standards/blob/8f818b7/standards/SWSS/v1.0.md) section by section. These historical links use an accepted commit because the original issue's source branch has been deleted. The root draft is removed only after reconciliation; Git history preserves it.

On 2026-10-18, the read-only application checkouts matched their remote `main` heads:

- **SimShelf:** [`1aceecb3febf6e8e193fdc99d756ed345820d83c`](https://github.com/mongstad/SimShelf/tree/1aceecb3febf6e8e193fdc99d756ed345820d83c). Checked `docs/DATA.md`, `docs/PROGRESS.md`, `docs/PARAMETER_DISCOVERY.md`, the scalar-field example/configuration and `src/simshelf/recording.py` for output inheritance and metric validation.
- **Wavez:** [`681a46f8f8473ee6b5323ec4af71ada883183077`](https://github.com/mongstad/Wavez/tree/681a46f8f8473ee6b5323ec4af71ada883183077). Checked `WAVEZ_API.md`, `docs/WVZ1_FORMAT.md`, `docs/CAPTURE_FORMAT_POLICY.md` and `docs/SIMULATION_INTEGRATION_GUIDE.md` for geometry, scientific meaning, writer failure and readback contracts.

The specification links to current application documentation for ongoing use; the revisions above identify the evidence for this review.

## Old-to-new reconciliation

Destinations refer to sections of the authoritative draft.

| Original detailed section | Destination and decision |
| --- | --- |
| 1. Purpose and principles | §§1–2: retain scientific authority, no silent numerical changes, no overwrite, and gradual adoption. Retain the modular draft's independent name and profiles; exclude the original implication that every compliant simulation requires both tools. |
| 2. Compatibility baseline | §§3–4: retain entry point, literal version label, parameter discovery/schema, output alignment, WVZ1 geometry and tested export path. Do not prescribe a universal `--output` priority: joining inherits the recorder target, and conflicting destinations must be resolved or rejected explicitly. Retain the modular draft's required representative viewer inspection. |
| 3. Scientific version/source identity | §§2–3: restore every accepted source-package change (including comments/configuration), while distinguishing exact snapshots, structural fingerprints and human labels. Mandatory labels and per-change bumps are SWSS house rules, not SimShelf defaults. Proposed checks cannot auto-edit research source. |
| 4. Progress and measurements | §§2–3: restore indeterminate stages, rate limits, diagnostic applicability, formulas/units, sampled timestamps, nonfinite handling and independent CSV/JSON. Both progress paths require enabled libraries; Step counts is selected explicitly. Process-completion display values are not measured progress or science. |
| 5. Logs and automatic capture | §§2–3: require unique timestamped `.log` files and automatic Files capture with no manual upload; retain native Logs separately. Restore ordered copy-rule example, size-budget checks, incomplete-capture reporting and retention guidance. The local second-handler mirror is optional, as in the modular draft: only the effective output copy is necessary for capture. No external-log feature is assumed. |
| 6. Output organization/naming | §§2–3: restore a readable timestamped layout, collision-resistant IDs, source exclusions, isolated capture folders and copy/reference guidance. Correct the modular example's plain `run.log`, which contradicted timestamped filenames. Large binaries SHOULD remain outside Git, retaining the modular recommendation rather than an unconditional ban. |
| 7. Provenance/reproducibility | §2: restore simulation name, Python version, solver settings, physical/diagnostic distinctions and reproduction limitations. `summary.json` remains recommended; when present it must preserve quantity meanings. Core provenance does not require that particular container. |
| 8. Interruption/failure/performance | §§2, 4: restore closure of measurements/writers, handled interruption reasons, truthful partial artifacts, checkpoint lineage and independent scientific archives. Separate solver, diagnostic, recording and restart cadences; WVZ1 is not restart state. Add documented writer-failure limits and explicit readback coverage. |
| 9. Acceptance checklist | §5 and review gates: apply checks only to claimed profiles; retain concurrent runs, independent metric comparisons, budgets, failure/cancellation, baseline and backup checks. Require payload readback rather than treating successful viewer playback as an integrity guarantee. |
| 10. Adoption/out-of-scope | §5: retain one synthetic pilot, separately approved future helper/template work, no mass migration or historical rewrite, and explicit exclusions for automatic bumping, external logs, database embedding, cloud upload and video/restart claims. |
| 11. References | §6: retain current authoritative contracts, restore the scientific integration guide and example capture configuration, and record immutable reviewed revisions here. Avoid copying the complete app API or wire format. |

## Validation boundary

This change reconciles documentation and checks contract statements, Markdown paths/anchors, capture-fragment TOML syntax, profile consistency and the documentation-only diff. It does **not** execute a scientific pilot, prove automatic capture in a live run, enable a SimShelf library, exercise cancellation, create WVZ1 files or inspect the viewer. Those checks remain unchecked in the [review gates](REVIEW.md).

Owner review is still needed for the proposed version-bump policy, profile requirements and eventual pilot evidence. Licensing, ratification and publication remain separate owner decisions.

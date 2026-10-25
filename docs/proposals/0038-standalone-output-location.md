# Standalone output location — SWSS v3.0 proposal

**Draft contract proposal, not the current specification.** [SWSS v2.0](../../standards/SWSS/v2.0.md) remains authoritative. This document proposes a breaking baseline revision, SWSS **v3.0**, and portable metadata schema **3** with optional output-parent declarations. Accepted schema 2 is unchanged. Its MUST/SHOULD/MAY wording describes the proposed revision only. It neither changes existing conformance claims nor declares an implementation conformant.

## Revision and metadata decision

The new default narrows the layouts permitted by v2.0 §2.5. It therefore belongs in a major SWSS revision, even though it does not change the scientific computation. A v2.0 simulation with a different documented output parent remains v2.0 compliant if it satisfies that revision; it does not automatically claim v3.0.

Propose optional portable **`swss.output_parent`** and **`swss.output_parent_parameter`** fields in schema 3. A static declaration lets independent consumers discover the authored standalone parent; the parameter binding lets them account for explicit CLI overrides without guessing option names or executing source. A field alone would leave runtime overrides unresolved; documentation alone would require every consumer to maintain a local mapping. Absolute workstation paths in metadata would reduce portability. The proposed combination keeps the declared parent root-relative and permits explicit external destinations through the bound CLI parameter or reviewed manual launch configuration.

Schema 3 is necessary even though the fields are optional: schema 2 rejects unknown `[swss]` fields and does not give an omitted output field any meaning. No universal CLI spelling, environment variable, extension identifier, coordination transport or extra companion file is introduced. `simulation_version` still identifies the simulation source revision, not the metadata schema or SWSS revision. Schema-3 validity establishes the declaration's meaning, not full baseline conformance or actual runtime behavior.

## Proposed schema-3 output declaration

Schema 3 retains the schema-2 tables, parameter-row semantics, exact-argv rules, source bindings, data-only discovery, extension isolation and all safety/resource bounds in v2.0 §4, except for the required schema integer becoming `3` and these two optional fields. Unknown `[swss]` fields still invalidate the document. Existing entrypoint/source paths remain contained regular-file paths; the new parent is a directory path and MAY be absent at discovery time.

| Field within `[swss]` | Proposed requirement |
| --- | --- |
| `output_parent` | Optional nonempty root-relative directory path; omission means `outputs`. A supplied value is an explicit author-selected standalone-parent override. It identifies a shared parent, never a full run root. |
| `output_parent_parameter` | Optional parameter ID naming the sole declared CLI control for a runtime parent override. Omission means no portable CLI binding, not permission to infer one from names/help/defaults. |

The parent MUST use `/` separators and relative components: no leading/trailing separator, empty component, `.`, `..`, backslash, drive/URI prefix, control character or expansion syntax (`~`, `$`, `*`, `?`, `[` or `]`). It is limited to **1,024 UTF-8 bytes**. Resolve it beneath the selected simulation root independently of working directory; apply containment, symlink, source-overlap and identity checks below. Absolute/external paths are intentionally not portable metadata values. They remain valid explicit launch overrides subject to platform/path checks. Discovery MUST NOT create the parent, allocate a run, probe an external volume, import source, invoke the program or write configuration.

`output_parent_parameter` MUST match the existing parameter-ID grammar and reference one valid row with `kind = "option"`, `type = "string"`, `action = "store"`, `required = false`, no `choices`, and `repeatable` absent or false. Its aliases use the existing exact-option grammar. If the row declares an informational `default`, it MUST equal the declared `output_parent` text (or `outputs` when omitted); consumers MUST NOT substitute that hint for the parent field. The simulation MUST use the declared parent when the option is absent and the explicit option value when present, without requiring the consumer to insert default tokens. Invalid field types/paths, missing or ineligible linked rows, or inconsistent default hints invalidate the whole schema-3 document with a visible diagnostic and manual fallback. Unrelated row errors retain the existing manual-row rules.

This is an author-maintained behavior declaration, not permission for a launcher to redirect an arbitrary script. Authors MAY read their own companion at execution or maintain matching source behavior, but MUST validate agreement and bump the simulation source version for source-package changes. A metadata edit alone does not change a parser's default or prove its behavior. All other declared controls MUST leave output placement unchanged; destination changes driven by unmodeled inputs, environment, configuration or solver state require explicit manual configuration rather than automatic routing.

### Resolving the effective parent without changing argv

Automatic resolution requires associated, valid, supported schema-3 metadata, acceptable source binding under the existing rules, safe paths, and unambiguous launch arguments. When no source hashes are supplied, show **binding unverified**, never verified behavior; a supplied stale/unsafe/over-budget binding disables automatic routing as well as typed use. Resolve only the following conservative subset:

1. With no explicit bound option, use `output_parent`, or root-relative `outputs` if omitted. This default applies only to schema 3; a schema-2 document never implies it.
2. Recognize one exact occurrence of a bound alias before the first `--`: long `--name=value`, long `--name value`, or short `-o value`. Split at the first `=` for interpretation only; preserve the original tokens. A nonempty relative override resolves against the selected root; an absolute override may select external storage. A value-looking option token cannot be consumed as a path without an unambiguous mapping.
3. Missing/empty values, repeats (even with equal values), short bundles/attached short values, post-delimiter content, unknown or manual-only tokens, and uncertain token ownership MUST disable automatic resolution. Do not choose a last occurrence or use the declared/default parent despite unresolved intent. Preserve argv and require an explicit reviewed manual parent/root mapping or correction. Other fully supported declared scalar/flag arguments may coexist without affecting the parent.
4. A manual/local destination selection MUST agree with the computed parent or produce a conflict requiring explicit correction before a launch claiming automatic routing. It MUST NOT silently supersede argv or metadata. An unmapped author override remains available through explicit manual configuration, with automatic resolution visibly unavailable for that launch. Standalone execution remains independently available.

Validate paths and required external-volume availability at launch before source enumeration or run allocation. A changed whole companion, supplied source binding, argv, selected root/entrypoint or local destination MUST invalidate the destination preview; re-resolve and recheck before use without rewriting tokens or historical records. Preserve the exact declaration bytes/hash, schema, parent value/default origin, binding ID, consumed token span, resolution mode, resolved destination, binding diagnostics and check timing with run provenance. Matching declared/source bytes does not certify correct output behavior.

## Proposed replacement for baseline output placement

These requirements would replace v2.0 §2 item 5 and qualify its suggested layout. All other baseline obligations, including exact argv, scientific integrity, versioning, logs and truthful lifecycle, carry forward unchanged.

### Selected root and default parent

1. A simulation claiming v3.0 MUST document how its simulation root is selected before execution. The root is an explicitly selected project directory. When portable configuration is used, it is the directory containing the associated `swss.toml`, whose root-relative entrypoint MUST match the selected program. The root MUST NOT be inferred by walking parents, by the process working directory alone, or by assuming the directory of a nested Python entrypoint.
2. Baseline-only simulations MAY omit `swss.toml`. Their documented invocation MUST still establish an explicit root, and a launcher MUST obtain that root through author instructions and reviewed launch configuration. If root selection or association is ambiguous, a launcher MUST decline the v3.0 placement claim and request an explicit configuration; it MUST NOT guess or silently change the selected program.
3. Without an explicit effective run-root agreement or output-parent override, the simulation MUST use `outputs/` immediately beneath the selected root as its standalone output parent. A supplied schema-3 `output_parent` is an explicit author-selected parent override; omission preserves `outputs/`. This default is independent of the launch working directory. A root-level entrypoint therefore has `outputs/` beside it; a nested entrypoint uses the project root's `outputs/`, not its own directory.
4. Each standalone execution MUST exclusively allocate one new timestamped, collision-resistant child directory beneath the effective parent before writing run evidence. Its identity MUST be independent of the scientific RNG and correlate logs, artifacts and provenance. Use atomic no-replace creation or equivalent protection; checking existence alone is insufficient. Successive and concurrent executions MUST have distinct, non-overlapping roots. A selected child collision MUST fail without replacing existing evidence or silently choosing another child. A deliberate retry is a new execution with a new identity.

### Explicit override and precedence

Authors MUST document an explicit output-parent override suitable for external storage, including its option spelling, path resolution, validation, and how the effective parent is communicated to launchers/recorders before source capture. With schema 3, authors SHOULD bind an eligible override parameter using `output_parent_parameter` to permit automatic resolution. Other override interfaces require reviewed manual configuration. An override selects a **parent**, not an existing run root. Standalone execution still creates exactly one unique child.

Precedence is:

| Input | Effective destination |
| --- | --- |
| Explicit, supported and acknowledged coordinated run root | Use that full root directly under the coordinated-capture rules below. |
| No coordinated root; explicit runtime output-parent override | Allocate one unique child beneath that parent, superseding the metadata parent/default. |
| Neither above; supplied schema-3 `output_parent` | Allocate one unique child beneath the declared root-relative parent. |
| None of the above | Allocate one unique child beneath `<selected-root>/outputs/`. |
| Conflicting or unsupported coordination, or ambiguous destination | Fail clearly before run-output writes; do not fall back silently. |

Under this proposal, a relative override MUST resolve against the selected simulation root, never the working directory; an absolute override MAY select another volume. Empty values, control characters, traversal components (`..`), shell/URI expansion, and inaccessible or non-directory existing components MUST be rejected. Literal path values MUST NOT expand `~`, environment variables or globs. A nonexistent parent MAY be created only after validation and explicit selection. Existing parent contents MUST remain untouched. Permission, collision and storage errors MUST produce distinct useful diagnostics and nonzero status; partial new evidence MUST be retained truthfully.

For an override requiring a particular external volume, the author/launcher contract MUST state how availability and volume identity are verified before parent creation. An absent mount MUST NOT cause writes to a same-named directory on the underlying filesystem. Record the check and disclose platform limits; a path string alone does not prove the intended volume is mounted.

The simulation and launcher MUST agree on the resolved effective parent before source snapshots or scientific writes. An override known only to the simulation is insufficient for a launch claiming source separation. Use the schema-3 mapping when valid and unambiguous, or retain a reviewed manual mapping; a parameter name or default hint alone establishes neither. Discovery MUST NOT insert default or override tokens. Unchanged tokens remain unchanged; resolved paths are separate provenance.

### Coordinated capture remains optional

v2.0 §3.1's direct-root rule carries forward: a launcher and a simulation claiming coordinated capture MUST explicitly agree on one full unique effective run root before writing, and document supply, acknowledgement, allocation ownership and compatibility. The simulation MUST use that root directly, without allocating a second run directory beneath it. Artifact subdirectories remain allowed. The standalone default applies only when no effective run root is supplied.

The agreement MUST distinguish a shared parent from a full run root. It MUST establish the effective output-parent exclusion boundary before source capture, including earlier sibling runs, and assign exclusive ownership of the new root without relying on observed emptiness. Roots MUST be distinct and non-overlapping across executions. Existing unrelated contents, an occupied claim or incompatible allocation ownership MUST cause failure without mutation. Explicit destination arguments MUST agree with the declared parent/root roles or fail before output writes; an unsupported root request MUST NOT be ignored in favor of standalone allocation.

Schema-3 output fields describe standalone **parent** selection only. They neither request a full run root nor acknowledge a coordinated agreement. A separately supported agreement MUST explicitly establish any replacement parent and reconcile runtime destination arguments before snapshotting; it may supersede the standalone metadata parent but MUST retain other known generated-tree exclusions. Without that agreement, the simulation owns child allocation and the launcher watches the effective parent.

Valid metadata in either schema, output-parent declarations, matching source hashes, baseline compliance, and successful process exit MUST NOT be treated as evidence of this optional capability. A launcher MUST NOT preallocate a second run root for an ordinary standalone simulation. Watching a shared parent alone does not prove per-process attribution during concurrent capture; recorders MUST document and validate their attribution or reject unsupported overlap. Solver completion and capture completeness remain separate.

## Proposed source-snapshot boundary requirements

These requirements apply whenever a source snapshot/version comparison is produced for a v3.0 run, whether or not coordinated capture is claimed. They strengthen the existing generated-tree exclusion rule without authorizing omission of research source.

- Before enumerating, reading or hashing source, the snapshotter MUST establish and recursively exclude the **effective output parent**, including all older sibling runs and the current root. It MUST retain other explicitly known output boundaries relevant to the selected source tree; a launch override MUST NOT erase a registered or previously reviewed generated-tree boundary. A full current run root alone is insufficient.
- Exclusions MUST follow canonical path containment, not substring/prefix matching or folder-name heuristics. A similarly named research directory outside an excluded tree MUST remain eligible. The snapshotter MUST NOT classify copied entrypoints or generated JSON as research source merely because of their extensions.
- Research source, applicable `swss.toml`, and required input/configuration files MUST remain eligible under the documented source policy. A parent equal to/above the simulation root, or overlapping required research inputs, MUST be rejected as an unsafe output selection rather than silently dropping research files. If source/output roles overlap, require an explicit corrected layout before launch. Do not infer ownership from names, emptiness or content.
- Resolve the selected root once with user knowledge. Reject symlinks in output destination components and aliases that escape or overlap protected source/input trees; validate existing ancestors for absent destinations. Recheck identity at allocation and snapshot access. If safe separation cannot be established, fail before output writes rather than weakening checks. Implementations MUST document residual replacement races and tested filesystem/platform limits; static path checks alone do not establish isolation against hostile concurrent mutation.
- Record the selected SWSS revision, root association, effective parent, actual run root, allocation mode, exclusion boundaries and their configuration source/check timing with the run's provenance. Retain exact argv separately. Use root-relative paths where possible; external-location records MUST use an access-controlled location record sufficient to resolve the actual destination, without embedding credentials or unnecessary machine paths in portable metadata.

Logs, process streams, capture policies, budgets, artifact identities and independent backups retain the obligations of the claimed capabilities. Excluding a generated tree from source is not permission to delete it, treat it as backed up, or report capture complete.

## Discovery limits

| Available evidence | What a consumer can establish |
| --- | --- |
| Associated valid schema-2 document | Selected root/entrypoint association and declared parameter metadata; no output location or baseline/capture claim. |
| Associated valid schema-3 document, no output fields, unambiguous argv | Declared standalone default `<root>/outputs`; no implied coordinated-root support or baseline certification. |
| Schema-3 `output_parent`, with or without a valid parameter binding | Authored parent; a bound unambiguous CLI override supersedes it. Unresolved arguments/configuration require manual resolution, never fallback to the declaration. |
| Parameter row with a name/help/default suggesting outputs | An informational CLI declaration only; no standardized path role or resolution base. |
| Source-file hashes match | Listed bytes match; no proof of output behavior, complete source binding or coordinated capture. |
| Explicit v3.0 claim plus reviewed author invocation/root/output contract | The default/override can be configured for that revision; implementation evidence is still required for conformance. |
| Script without a companion, or invalid/stale/unassociated metadata | Manual author instructions and reviewed configuration are needed; no directory guessing, recursive metadata search or automatic v3.0 adoption. |

Consumers MUST preserve metadata diagnostics/manual fallback, and distinguish metadata validity, source binding, resolved output location and tested workflow conformance. Independent launch safety checks still apply. Existing source snapshots with unexplained generated files cannot be repaired by assuming a directory name identifies outputs. No companion or unsupported metadata means no portable automatic discovery, even when an author documents a v3.0 baseline claim.

## Layout examples

Illustrative paths and names below do not standardize a transport or CLI spelling.

```text
experiment/                         # explicitly selected root
  swss.toml                         # entrypoint = "solver/simulate.py"
  solver/simulate.py
  inputs/initial.json                # retain as research input
  outputs/                          # standalone default; prune whole tree from source
    run_20261025T120000Z_A/
    run_20261025T120001Z_B/
```

Launching from another directory still uses `experiment/outputs/`. For a root-level `simulate.py`, the same `outputs/` is beside that file. The accepted scalar-decay reference currently resolves relative parents against its working directory and implements no coordinated-root agreement; it remains a v2.0 example and is not a v3.0 implementation.

An adopting simulation may declare a custom project-local parent and its runtime override with the following complete schema-3 example. The CLI spelling is illustrative; the two portable field names and their semantics are proposed contract. Omitting `output_parent` and changing the optional row default to `outputs` restores the standard default; omitting both output fields and the row also permits default discovery for an empty argv.

```toml
[swss]
schema_version = 3
entrypoint = "solver/simulate.py"
simulation_version = "0.2.0"
output_parent = "results/standalone"
output_parent_parameter = "destination"

[[swss.parameters]]
id = "destination"
kind = "option"
options = ["--output-parent", "-o"]
required = false
type = "string"
action = "store"
help = "Parent for unique run directories; relative paths use the selected project root"
default = "results/standalone"
```

With no destination token, the declared parent is `experiment/results/standalone/`. With exact argv `["--output-parent", "/research-volume/experiment-results"]`, the bound override selects external storage without editing the companion or normalizing those tokens. With repeated destination options, automatic discovery declines; it does not guess the parser's last-wins behavior.

For that external override, a standalone run uses `/research-volume/experiment-results/run_20261025T120002Z_C/`. Source capture retains `experiment/solver/`, `inputs/` and `swss.toml`; it excludes the external generated parent wherever reachable by its source selection, along with other known generated boundaries. A missing or unwritable volume produces a failure, not a fallback into the project.

If a separately supported coordinated agreement supplies `/research-volume/experiment-results/run_20261025T120003Z_D/`, the simulation writes directly there. It MUST NOT create `.../D/run_.../`. Merely passing a standalone parent option pointing at `.../D/` is not such an agreement and would instead request a standalone child.

## Adoption and conformance

### Reader compatibility

| Reader and document | Required behavior |
| --- | --- |
| Existing schema-2 reader; schema-2 document | Existing metadata behavior; no automatic output semantics. Adding either new field under schema 2 remains invalid. |
| Existing schema-2 reader; schema-3 document, even with both optional fields omitted | Unsupported-version diagnostic and explicit manual fallback; no field stripping, downcasting or reinterpretation as schema 2. |
| Reader explicitly supporting schema 3 and schema 2; schema-2 document | Apply schema-2 rules only; do not infer `outputs` or synthesize a binding. |
| Reader explicitly supporting schema 3; schema-3 document | Implement the new default/fields, output resolution and safeguards in addition to retained metadata obligations. A parameter-only reader may avoid output operations but MUST NOT claim automatic output resolution. |
| Unsupported future schema or malformed/unsafe schema-3 document | Visible diagnostic, no automatic routing or typed metadata reuse, and preserved argv/manual path subject to independent safety checks. |

Support MUST be explicit per schema; partial parsing or an extension MUST NOT override these rules. Schema-3 adoption opts into the declaration/default semantics, not a full SWSS baseline/capture claim. A baseline-only v3.0 simulation may still have no companion; schema-2 metadata may still accompany a manually configured simulation without acquiring the new declaration semantics. No application can infer a simulation's entire claimed SWSS revision from `schema_version` alone.

### Deliberate adoption

Adoption is explicit per simulation/tool and new run. Before authoring a schema-3 companion, review actual default/override behavior, bind the correct optional string parameter if possible, and validate it from another working directory and with explicit external storage. A schema-number edit alone is not a migration: align the simulation with the declared root-relative behavior and default, update its source-package version and any supplied hashes deliberately, and confirm consumers support schema 3 before using it. Keep the chosen SWSS revision distinct, and validate scientific equivalence and exact argv. Do not automatically move outputs, convert saved configurations, relabel old runs, regenerate historical snapshots, or rewrite previously recorded source/configuration/argv/artifacts. A new clean snapshot may differ from an old contaminated baseline; preserve and explain both records.

A v2.0 simulation's custom output location remains valid under its original claim. The unchanged schema-2 document alone cannot opt it into these rules. Consumers MUST preserve deliberate v2.0/manual workflows and require explicit review of new-run configuration when adopting v3.0. Retire an old reader only after affected paths are validated under the existing specification-first adoption rules.

The [conformance fixtures](fixtures/0038-output-location.md) define positive/negative cases and required evidence, including schema compatibility, declared/default parents, bound runtime overrides and unresolved routing. They are test specifications, not executed v3.0/schema-3 implementation evidence. No reference implementation, consumer migration, coordination wire format or scientific certification is supplied by this proposal. Automatic discovery establishes an expected parent under a validated author declaration; it does not prove where arbitrary code actually writes or authorize source exclusions that hide required research files.

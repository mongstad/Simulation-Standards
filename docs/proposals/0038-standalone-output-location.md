# Standalone output location — SWSS v3.0 proposal

**Draft contract proposal, not the current specification.** [SWSS v2.0](../../standards/SWSS/v2.0.md) remains authoritative. This document proposes a breaking baseline revision, SWSS **v3.0**, with portable metadata schema **2 unchanged**. Its MUST/SHOULD/MAY wording describes the proposed revision only. It neither changes existing conformance claims nor declares an implementation conformant.

## Revision and metadata decision

The new default narrows the layouts permitted by v2.0 §2.5. It therefore belongs in a major SWSS revision, even though it does not change the scientific computation. A v2.0 simulation with a different documented output parent remains v2.0 compliant if it satisfies that revision; it does not automatically claim v3.0.

Use a **documented author-provided output-parent parameter**, rather than adding a portable metadata field in this revision. The author defines the exact option spelling and value semantics. No universal CLI option, environment variable, extension identifier or coordination transport is introduced. This permits external storage without turning schema-2 parameter descriptions into executable routing instructions. A future machine-readable output declaration requires a separate explicit schema decision and conformance cases; it MUST NOT be smuggled into schema 2 or an allegedly portable extension.

Schema 2 continues to describe portable metadata and optional parameter rows, not the SWSS baseline revision or output ownership. `simulation_version` identifies the simulation source revision, not SWSS v3.0. Adding an unknown `[swss]` output field still invalidates portable metadata under v2.0 §4.2. No new companion file is required.

## Proposed replacement for baseline output placement

These requirements would replace v2.0 §2 item 5 and qualify its suggested layout. All other baseline obligations, including exact argv, scientific integrity, versioning, logs and truthful lifecycle, carry forward unchanged.

### Selected root and default parent

1. A simulation claiming v3.0 MUST document how its simulation root is selected before execution. The root is an explicitly selected project directory. When portable configuration is used, it is the directory containing the associated `swss.toml`, whose root-relative entrypoint MUST match the selected program. The root MUST NOT be inferred by walking parents, by the process working directory alone, or by assuming the directory of a nested Python entrypoint.
2. Baseline-only simulations MAY omit `swss.toml`. Their documented invocation MUST still establish an explicit root, and a launcher MUST obtain that root through author instructions and reviewed launch configuration. If root selection or association is ambiguous, a launcher MUST decline the v3.0 placement claim and request an explicit configuration; it MUST NOT guess or silently change the selected program.
3. Without an explicit effective run-root agreement or output-parent override, the simulation MUST use `outputs/` immediately beneath the selected root as its standalone output parent. This default is independent of the launch working directory. A root-level entrypoint therefore has `outputs/` beside it; a nested entrypoint uses the project root's `outputs/`, not its own directory.
4. Each standalone execution MUST exclusively allocate one new timestamped, collision-resistant child directory beneath the effective parent before writing run evidence. Its identity MUST be independent of the scientific RNG and correlate logs, artifacts and provenance. Use atomic no-replace creation or equivalent protection; checking existence alone is insufficient. Successive and concurrent executions MUST have distinct, non-overlapping roots. A selected child collision MUST fail without replacing existing evidence or silently choosing another child. A deliberate retry is a new execution with a new identity.

### Explicit override and precedence

Authors MUST document an explicit output-parent override suitable for external storage, including its option spelling, path resolution, validation, and how the effective parent is communicated to launchers/recorders before source capture. An override selects a **parent**, not an existing run root. Standalone execution still creates exactly one unique child.

Precedence is:

| Input | Effective destination |
| --- | --- |
| Explicit, supported and acknowledged coordinated run root | Use that full root directly under the coordinated-capture rules below. |
| No coordinated root; explicit output-parent override | Allocate one unique child beneath that parent. |
| Neither | Allocate one unique child beneath `<selected-root>/outputs/`. |
| Conflicting or unsupported coordination, or ambiguous destination | Fail clearly before run-output writes; do not fall back silently. |

Under this proposal, a relative override MUST resolve against the selected simulation root, never the working directory; an absolute override MAY select another volume. Empty values, traversal components (`..`), shell/URI expansion, and inaccessible or non-directory existing components MUST be rejected. Literal path values MUST NOT expand `~`, environment variables or globs. A nonexistent parent MAY be created only after validation and explicit selection. Existing parent contents MUST remain untouched. Permission, collision and storage errors MUST produce distinct useful diagnostics and nonzero status; partial new evidence MUST be retained truthfully.

For an override requiring a particular external volume, the author/launcher contract MUST state how availability and volume identity are verified before parent creation. An absent mount MUST NOT cause writes to a same-named directory on the underlying filesystem. Record the check and disclose platform limits; a path string alone does not prove the intended volume is mounted.

The simulation and launcher MUST agree on the resolved effective parent before source snapshots or scientific writes. An override known only to the simulation is insufficient for a launch claiming source separation. Launch configuration MUST retain the reviewed mapping from author parameter to parent; neither a parameter named `output_parent` nor a default hint establishes that mapping. Absence of machine discovery does not authorize rewriting argv to insert the default or override. Unchanged tokens remain unchanged; resolved paths are separate provenance.

### Coordinated capture remains optional

v2.0 §3.1's direct-root rule carries forward: a launcher and a simulation claiming coordinated capture MUST explicitly agree on one full unique effective run root before writing, and document supply, acknowledgement, allocation ownership and compatibility. The simulation MUST use that root directly, without allocating a second run directory beneath it. Artifact subdirectories remain allowed. The standalone default applies only when no effective run root is supplied.

The agreement MUST distinguish a shared parent from a full run root. It MUST establish the effective output-parent exclusion boundary before source capture, including earlier sibling runs, and assign exclusive ownership of the new root without relying on observed emptiness. Roots MUST be distinct and non-overlapping across executions. Existing unrelated contents, an occupied claim or incompatible allocation ownership MUST cause failure without mutation. Explicit destination arguments MUST agree with the declared parent/root roles or fail before output writes; an unsupported root request MUST NOT be ignored in favor of standalone allocation.

Valid schema-2 metadata, matching source hashes, baseline compliance, and successful process exit MUST NOT be treated as evidence of this optional capability. A launcher MUST NOT preallocate a second run root for an ordinary standalone simulation. Watching a shared parent alone does not prove per-process attribution during concurrent capture; recorders MUST document and validate their attribution or reject unsupported overlap. Solver completion and capture completeness remain separate.

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
| Parameter row with a name/help/default suggesting outputs | An informational CLI declaration only; no standardized path role or resolution base. |
| Source-file hashes match | Listed bytes match; no proof of output behavior, complete source binding or coordinated capture. |
| Explicit v3.0 claim plus reviewed author invocation/root/output contract | The default/override can be configured for that revision; implementation evidence is still required for conformance. |
| Script without a companion, or invalid/stale/unassociated metadata | Manual author instructions and reviewed configuration are needed; no directory guessing, recursive metadata search or automatic v3.0 adoption. |

Consumers MUST preserve metadata diagnostics/manual fallback under the current contract, and distinguish metadata validity, source binding and tested workflow conformance. Independent launch safety checks still apply. Existing source snapshots with unexplained generated files cannot be repaired by assuming a directory name identifies outputs.

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

For external storage, suppose an author documents `--output-parent /research-volume/experiment-results` and the launcher explicitly records that mapping. A standalone run uses `/research-volume/experiment-results/run_20261025T120002Z_C/`. Source capture retains `experiment/solver/`, `inputs/` and `swss.toml`; it excludes the external generated parent wherever reachable by its source selection, along with other known generated boundaries. A missing or unwritable volume produces a failure, not a fallback into the project.

If a separately supported coordinated agreement supplies `/research-volume/experiment-results/run_20261025T120003Z_D/`, the simulation writes directly there. It MUST NOT create `.../D/run_.../`. Merely passing a standalone parent option pointing at `.../D/` is not such an agreement and would instead request a standalone child.

## Adoption and conformance

Adoption is explicit per simulation/tool and new run. Review existing layout, relative-path semantics, required source/input locations, output override and recorder boundaries before changing a claim. Bump the simulation source version when its source package changes, keep the chosen SWSS revision distinct, and validate scientific equivalence and exact argv. Do not automatically move outputs, convert saved configurations, relabel old runs, regenerate historical snapshots, or rewrite previously recorded source/configuration/argv/artifacts. A new clean snapshot may differ from an old contaminated baseline; preserve and explain both records.

A v2.0 simulation's custom output location remains valid under its original claim. The unchanged schema-2 document alone cannot opt it into these rules. Consumers MUST preserve deliberate v2.0/manual workflows and require explicit review of new-run configuration when adopting v3.0. Retire an old reader only after affected paths are validated under the existing specification-first adoption rules.

The [conformance fixtures](fixtures/0038-output-location.md) define positive/negative cases and required evidence. They are test specifications, not executed v3.0 implementation evidence. No reference implementation, consumer migration, coordination wire format or scientific certification is supplied by this proposal. The decision to add portable output-routing metadata is explicitly deferred to a separately scoped schema revision; manual author-contract mapping is the interoperability limit of this design.

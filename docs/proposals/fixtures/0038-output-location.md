# Output-location conformance fixtures

These black-box fixtures accompany the [SWSS v3.0 proposal](../0038-standalone-output-location.md). They specify tests for an implementation adopting that proposal; they do not change [current v2.0 conformance](../../../standards/SWSS/v2.0.md#5-conformance-and-evidence). No v3.0 implementation is exercised by this document.

## Fixture setup and evidence

Use a disposable sandbox with the following logical paths. `PROJECT`, `OTHER` and `VOLUME` are harness-assigned absolute directories, not protocol variables or paths to real research data. `VOLUME` may initially be another sandbox directory; an actual separate-volume test must identify its filesystem/mount and is required before claiming that coverage.

```text
PROJECT/
  swss.toml                         # schema 2; entrypoint = "solver/model.py"
  solver/model.py                   # harmless implementation under test
  solver/helper.py                  # legitimate research source sentinel
  inputs/initial.json               # legitimate research input sentinel
  outputs/run_old/model.py          # generated copy, not source
  outputs/run_old/provenance.json   # generated sentinel
  outputs_notes/analysis.py         # legitimate similarly named source
OTHER/                              # launch working directory
VOLUME/results/run_old/summary.json # external historical evidence
```

Minimal companion contents (no parameter or output declaration):

```toml
[swss]
schema_version = 2
entrypoint = "solver/model.py"
simulation_version = "0.1.0"
```

The trusted test simulation must document its root-selection interface, parent-override option and any separately claimed coordination adapter. Use the actual documented interfaces, with no invented universal flags. It writes a deterministic small scientific result, log and provenance/summary into its actual run root; a copy of its entrypoint in generated output tests source separation. A snapshotter is separately required for snapshot cases, and a recorder for capture cases. Unsupported optional coordination is reported as untested, not passed.

Before each case, save bytes and hashes of all historical outputs, legitimate source/input files, companion bytes and exact invocation tokens. Afterward retain process status/streams, observed parent/root allocation, run identity, new evidence bytes, source manifest and compared digests, capture outcomes where claimed, and validation diagnostics. All existing sentinels must remain byte-identical. Expected failure means nonzero status, no scientific output writes and no mutation of existing evidence; a harmless newly created empty parent is not a successful run. Exercise process failure/interruption separately: preserve any new partial evidence and report it incomplete.

## Standalone allocation and source separation

| Case | Action | Required observation |
| --- | --- | --- |
| S1: nested entrypoint, foreign working directory | Select `PROJECT`, launch `solver/model.py` from `OTHER`, omit destination options. | Exactly one new timestamp/ID child under `PROJECT/outputs`; none under `OTHER` or `PROJECT/solver/outputs`. Record default mode and actual root; exact argv unchanged. |
| S2: successive runs | Execute S1 twice without source/metadata edits; take a source snapshot before each execution. | Two different children; no overwrite. Neither old nor current generated children enter source reads/hashes/manifests. Source comparison remains unchanged. |
| S3: simultaneous runs | Start two S1 executions with overlapping lifetimes, synchronizing at allocation if possible. | Atomic exclusive allocation of two non-overlapping roots; identical deterministic scientific results; distinct identities. Shared-parent recorder attribution requires independent evidence. |
| S4: forced collision | Inject a fixed timestamp/ID or use an equivalent allocation fault; prepopulate the resulting child. | Collision fails, does not select a replacement child, and preserves all existing bytes. Verify atomic no-replace creation, not just an existence check. |
| S5: explicit internal override | Document/select `results/nested` relative to `PROJECT`; populate it with a prior generated child; launch from `OTHER`. | One new child under `PROJECT/results/nested`; whole effective parent excluded before source reads. Previously known `PROJECT/outputs` remains excluded; no reset to current root only. |
| S6: explicit external override | Select absolute `VOLUME/results`; launch twice with unchanged inputs. | Two unique children there, none in default/working directories. Older external evidence remains unchanged, source manifests remain stable, actual destination and reviewed mapping retained. |
| S7: retained research files | Snapshot after S2/S5; then separately change `helper.py`, `initial.json`, and `outputs_notes/analysis.py`. | All three files and associated companion retained; each genuine change remains detectable under documented comparison semantics. Generated copies of `.py` and `.json` stay excluded. Restore fixture source between cases, never rewrite recorded snapshots. |
| S8: root-level entrypoint | Use an independent variant with `entrypoint = "model.py"` and an explicitly selected root. | Default `outputs/` beside that file, independent of working directory. Do not change the selected program to achieve association. |
| S9: no companion | Remove the companion in a fresh variant; select root through the documented baseline invocation. Repeat with root unspecified/ambiguous. | Explicit baseline root works without metadata. Ambiguous launch cannot claim v3.0 placement; decline until reviewed configuration supplies the root, with no directory guessing. |
| S10: science and argv | Compare default/internal/external executions using identical scientific inputs, including `0010`, `--label=`, aliases and separate empty-string tokens if supported by the fixture. | Scientific results match the independent baseline; allocation consumes no scientific RNG. Exact supported token spellings/order survive in provenance; resolved paths/values are separate. |

## Coordinated roots and capability boundaries

| Case | Action | Required observation |
| --- | --- | --- |
| C1: supported direct root | Through a documented supported adapter, agree on full unused `VOLUME/results/agreed_A`, its parent exclusion and exclusive allocation owner before snapshotting. | Write directly into `agreed_A`, no second run child; logs/provenance identify that root. Old siblings excluded. Capture verifies required log bytes separately from process exit. |
| C2: concurrent agreement | Agree on two distinct roots, then repeat with the same root or ancestor/descendant roots. | Distinct non-overlapping roots work when claimed; shared/overlapping roots are rejected without mutation. An empty-directory observation alone cannot authorize ownership. |
| C3: incompatible explicit destination | Supply a coordinated root plus an explicit destination argument disagreeing with the adapter's documented parent/root role. | Fail before writes; no silent precedence, nested allocation or fallback. Test an agreeing argument separately according to that adapter's contract. |
| C4: standalone-only simulation | Use schema-2 metadata and matching source hashes with no coordination implementation. Configure ordinary parent capture. Separately request unsupported coordination. | Ordinary launch creates only its own child; launcher creates no empty sibling. Unsupported request rejected explicitly; metadata/hash validity never enables coordination. |
| C5: occupied root and failure | Supply a root with unrelated content or an existing exclusive claim; separately interrupt a newly claimed run and retry it. | Existing evidence preserved; occupied root/reuse rejected. New partial evidence remains incomplete; retry requires a new root. |
| C6: capture limits | Where a recorder is claimed, omit a required log or exceed its documented budget. | Solver status remains separate; capture incomplete with a reason. Source exclusion is not a capture/backup claim. |

## Negative paths, discovery and adoption

Run each path mutation independently against default, override or coordinated selection as applicable. Check both allocation and pre-snapshot validation boundaries.

| Case | Mutation | Required observation |
| --- | --- | --- |
| N1: unsafe parent | Empty override, `../escape`, URI, an existing file component, unreadable/unwritable parent or unavailable external volume. | Clear failure without fallback or modification. Test real denied access under an appropriate user or report fault injection honestly. |
| N1b: absent external mount | Declare a required volume identity, then make that volume unavailable while leaving a writable underlying mountpoint directory. | Availability/identity check refuses before parent creation; no output lands on the underlying filesystem. A same-named path is insufficient evidence. |
| N2: protected overlap | Parent equals `PROJECT`, its ancestor, `PROJECT/solver`, or `PROJECT/inputs`. | Reject before snapshot/output writes; do not silently exclude legitimate source/inputs or run with incomplete source evidence. |
| N3: symlink alias | Link an output component/absent destination ancestor to another tree, including a path back into source; attempt a source alias into generated output. | Reject unsafe destination/association; never follow the alias to recapture outputs as source or write into protected data. Canonical containment prevents prefix lookalikes from being excluded. |
| N4: identity substitution | Replace an ancestor between validation and allocation/snapshot access using a controlled test hook. | Detect/refuse at the documented recheck boundary; report any remaining race window and do not claim hostile-filesystem isolation from a static check. |
| N5: literal path syntax | Use literal `$NAME`, `~` or wildcard characters in an otherwise safe selected path; separately supply URI/shell-expansion requests. | No expansion or command execution. Literal legal names may be used only under documented validation; unsupported syntax diagnosed, never interpreted as code. |
| N6: no portable output field | Use the minimal companion, then add `output_parent` under `[swss]`; separately add an unknown generic extension. | Minimal schema 2 conveys no routing. Unknown portable field invalidates metadata with manual fallback. Unknown extension semantics ignored, never silently adopted as a portable output contract. |
| N7: stale/unassociated metadata | Change a bound source hash or mismatch the selected entrypoint; repeat with missing/unsupported companion. | Preserve diagnostics, argv and explicit manual path; no inferred output parent, coordinated support, verified binding or v3.0 claim. Independent safety checks remain active. |
| N8: legacy custom parent | Keep a v2.0 simulation's documented custom-parent and working-directory semantics in a fresh run configuration. | No automatic v3.0 adoption or argv/settings conversion. Original v2.0 claim assessed under v2.0; explicit migration reviewed before a v3.0 run. |
| N9: historical preservation | Retain an old contaminated source snapshot and run record; create new clean evidence after explicit adoption. | All old records/manifests/blobs/argv/configuration/output bytes unchanged. New snapshot differences explained without relabeling the old baseline. |

## Reporting limits

Report implementation revision, claimed SWSS revision/capabilities, OS/runtime/filesystem, tested cases, expected/observed outcomes and exclusions. Byte/hash checks must read actual evidence. A sandbox directory used as `VOLUME` is not a tested removable/network/multi-terabyte volume. Concurrent simulation allocation is not concurrent recorder attribution. Fault injection is not disk exhaustion, power-loss recovery or adversarial filesystem testing. These fixtures do not certify numerical validity, full baseline conformance, backup restoration or consumer compatibility by themselves.

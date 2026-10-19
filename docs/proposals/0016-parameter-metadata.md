# Proposal: optional declarative parameter metadata

**Status: Design proposal for owner review, 2026-10-19. Not an accepted SWSS amendment or implemented application feature.** Addresses [issue #16](https://github.com/mongstad/Simulation-Standards/issues/16). MUST, MUST NOT, SHOULD and MAY below describe the proposed contract only.

## 1. Compatibility decision and scope

Recommend an additive, optional **parameter metadata capability in a future SWSS 1.1**, with portable section `swss.schema_version = 1`. Adoption of that revision and schema requires separate explicit owner approval; this proposal does not create either. [SWSS v1.0](../../standards/SWSS/v1.0.md) remains unchanged. Existing Core, SimShelf, Wavez and Full users need no declaration to retain their existing compliance. No new profile, mandatory tool, solver behavior, storage migration or Wavez change is proposed.

The portable section describes command-line inputs for one entrypoint, not solver configuration, execution commands or a source of runtime defaults. One companion file can also hold separately namespaced application settings. SWSS owns the portable contract; applications adapt to it, independently of SimShelf or Wavez. The script remains authoritative for parsing, validation and scientific meaning. A consumer MUST describe metadata as advisory, not proof that a parameter works. Declaration support MUST NOT imply that a launcher can run the simulation safely or that its results are validated.

## 2. Location, association and precedence

The owner-selected design uses **one `swss.toml` at the simulation root**, containing a reserved `[swss]` section and optional `[apps.<application>]` tables. A Python simulation plus this one companion file MUST suffice for the proposed declarations and participating applications' project configuration; no second TOML file or generated shadow configuration is required. A root is an explicitly selected project directory, not one guessed by walking parents. One document describes one simulation entrypoint. Multi-entrypoint project orchestration is outside this proposal; no recursive discovery, includes, overlays or file merging is permitted.

The only portable discovery path is `swss.toml` directly beneath that root. Its `swss.entrypoint` MUST exactly match the selected launch entrypoint's normalized root-relative path. A mismatch disables typed use with an explanation; it never changes the selected program. The portable section MUST NOT select an interpreter, shell, executable, working directory or environment. Application settings are not executed or interpreted by portable metadata discovery.

### Owner decision and adoption

**`swss.toml` is the sole configuration file for participating simulations.** SWSS defines the portable contract; SimShelf will read it, with application settings under `apps.simshelf`. Other applications use their own namespaces. No continuing `simshelf.toml` support, dual-file selection/merging, migration wizard, automatic conversion, shadow configuration or rollback compatibility layer is required or specified. Portable discovery reads only `swss.toml`; other filenames are not candidate configuration sources.

Adoption is deliberate work in separately authorized implementation changes:

1. Update SimShelf's configuration reader and all affected launch, capture and discovery paths to consume the single `swss.toml` contract.
2. Update participating simulations' configuration files to that format: shared identity and parameters in `swss`, application settings in `apps.simshelf` or the appropriate namespace. Authors check their settings and argv; discovery MUST NOT write or convert configuration files.
3. Validate the complete application path and participating configurations before release. Once the new implementation is validated, remove the old reader outright. Do not release a partially converted application whose entry points disagree about the configuration file. No permanent compatibility adapter is needed.

Retiring configuration parsing MUST NOT alter or delete existing run records, historical source snapshots (including old configuration bytes), recorded argv, artifacts or scientific provenance. History remains evidence of what actually ran; do not rewrite it to the new format. Preserving historical evidence does not require using historical configuration as input to new runs. New runs use the new configuration and record their own provenance. The simulation script remains authoritative for argument parsing and scientific behavior.

Optional participation in this proposed capability does not change existing SWSS v1.0 compliance. It does not require a future SimShelf release to retain its old configuration reader. A missing `swss.toml` means no portable metadata is available; an application needing configuration for a new run reports that requirement rather than searching for or converting an old file. Manual argument editing remains available, subject to independent launch requirements.

The companion-file path and portable entrypoint/source-manifest paths MUST use `/` separators and relative components, excluding empty components, `.`, `..`, leading `/`, backslashes, drive/URI prefixes and control characters. Resolve within the selected root; reject symlinks in the candidate or any referenced path component, escapes, non-regular files and inaccessible paths. Do not expand `~`, environment variables or globs. A selected root itself may be canonicalized once with user knowledge; all checks then use that root. Recheck identity when reading to avoid a check/open substitution; if a consumer cannot establish safe access, it MUST decline metadata use, not weaken containment.

Proposed discovery and argv precedence:

1. **Existing/manual argv remains authoritative user intent.** Discovery never overwrites tokens, even when declarations change.
2. A valid `swss.toml` supplies portable parameter metadata. Consumers MUST NOT merge it with other configuration files, legacy JSON declarations or static discoveries. No alternative metadata file is required by this contract.
3. Absent, invalid, stale or unsupported metadata yields a visible diagnostic and manual fallback, without silently switching to another source. An application MAY separately offer explicitly selected, bounded static discovery; it MUST identify that source, preserve argv and not present it as the SWSS declaration. No static discovery implementation is required here.

Missing/invalid `[swss]`, entrypoint mismatch and unsupported schema versions disable typed use. A valid partial declaration remains the selected source: undeclared and unsupported options stay manual, rather than being silently supplemented from AST discovery. Duplicate keys are parse errors; duplicate parameter IDs or alias ownership are document-wide ambiguity errors, not last-wins rules. Independent application safety/configuration checks may still prevent launch; manual fallback is not a bypass for them.

## 3. Data schema

Use UTF-8 **TOML 1.0.0** syntax. Consumers MUST reject duplicate keys and invalid TOML, and accept only the following schema. TOML syntax is defined by the [TOML specification](https://toml.io/en/v1.0.0); all parameter semantics and limits are stated here. Only root tables `swss` and optional `apps` are allowed. Unknown fields or structures within `swss` invalidate portable metadata use; application-owned fields are handled separately below. New schema versions require explicit consumer support, not best-effort reinterpretation.

| Field within `[swss]` | Proposed requirement |
| --- | --- |
| `schema_version` | Required integer `1`, not a boolean or string. |
| `entrypoint` | Required root-relative regular-file path, bound to the selected entrypoint. |
| `simulation_version` | Required nonempty string identifying the declared simulation source revision; distinct from the schema version and SWSS revision. |
| `parameters` | Required array of parameter tables; zero through 128 entries. Empty means no typed declarations, not no CLI arguments. |
| `source_files` | Optional array of `{path, sha256}` tables, unique paths. Each hash is 64 lowercase hexadecimal characters over exact file bytes. If present, include the entrypoint. No other fields. |

`[[swss.parameters]]` contains the parameter rows below; optional `[[swss.source_files]]` contains bindings. A third-party consumer MUST be able to use these tables without installing or consulting any application. `swss.schema_version` versions only the portable section, not application schemas.

`apps` MUST be a table of application tables keyed by a stable lowercase ASCII identifier matching `[a-z][a-z0-9_-]{0,63}` (for example `simshelf`). Applications own their nested settings and any application schema-version field. All consumers MUST enforce whole-file syntax and resource limits, but portable readers MUST ignore application semantics, including unknown application names, fields or schema versions. They MUST NOT interpret application data as SWSS defaults, parameters, source bindings or executable instructions. An invalid application configuration may prevent that application's launch, but MUST NOT make otherwise valid portable metadata invalid for other tools. Malformed TOML or a whole-file safety-limit violation affects all readers because there is only one document.

Application sections MUST NOT redefine or override the portable entrypoint, simulation version, parameter declarations or argv semantics. Consumers MUST use the shared fields in `swss`; no precedence contest between duplicated definitions is specified. A consuming application MUST diagnose conflicting duplicates in its own section and decline use of that application configuration until resolved. Unrelated tools need not understand those fields. Capture/preview settings belong to the application namespace; their interpretation is an application responsibility, not new SWSS capture semantics. No application section is mandatory. Do not put credentials in this shared, source-captured file; use separately managed application credentials instead.

Each parameter requires `id`, `kind`, `required`, `type`, `action`, `help`; `options` or `name` depends on kind. Optional fields are `choices`, `default`, `repeatable` (boolean, defaults to false). No implicit `required`, `type` or `action` is inferred.

| Parameter field | Meaning and constraints |
| --- | --- |
| `id` | Stable within the entrypoint across revisions; ASCII `[a-z][a-z0-9_]{0,63}`. It is not a CLI token or Python destination. A changed scientific meaning SHOULD receive a new ID; renaming never migrates argv automatically. |
| `kind` | `option` or `positional`. |
| `options` | For options only: 1–8 exact case-sensitive aliases, no duplicates. Each matches `--[A-Za-z][A-Za-z0-9_-]*` or `-[A-Za-z]`. First alias is the preferred new-control spelling, never a replacement for saved aliases. `--`, embedded `=`, whitespace, short bundles and abbreviations are not aliases. |
| `name` | For positionals only: a descriptive ASCII identifier using the same grammar as `id`. It is a label, never emitted as a token. |
| `required` | Boolean: whether the parser requires presence, not whether a default hint exists. A supported value option always takes exactly one value when present, even if `required = false`. |
| `type` | `integer`, `float`, `string` or `boolean`. Booleans are no-value flags, not value-taking `true`/`false` options. |
| `action` | `store` for integer/float/string options; `store_true` or `store_false` for boolean options. Positionals use `store` and a non-boolean type but are manual-only. |
| `help` | Human-readable description, plain text; empty allowed, never interpreted as markup, templates or commands. |
| `choices` | Optional nonempty array of at most 100 distinct values of the declared type. Not supported for flags. An explicitly supplied default must be a member. |
| `default` | Optional scalar of the declared type, informational only. Absence means unknown; `default = ""` is a known empty-string hint. TOML has no null value: do not invent a sentinel for `None`. |
| `repeatable` | True marks the row manual-only. No append/count/collection serialization is specified. |

Integer hints/choices MUST be TOML integers in signed 64-bit range, excluding booleans. Float hints/choices MUST be finite TOML floats, excluding integers and booleans; use binary64 numeric equality for duplicate/membership checks (`-0.0` equals `0.0`). String hints/choices MUST be TOML strings. Flags permit only boolean defaults. A default need not equal the usual argparse implicit default, since parsers can override defaults; it never determines token presence.

For supported value controls, validate integer text against `[+-]?[0-9]+` and signed 64-bit range, and float text against `[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?` with a finite binary64 result. This is a deliberately narrow portable editing subset, not a claim about every parser's grammar. Preserve the original text after validation: `00192`, `+192`, `1e-3` and `0.001` are not interchangeable argv spellings. Choices compare parsed numeric values or exact string values; display labels cannot replace tokens. Other numeric forms remain possible through manual editing, subject to the script's parser.

Positionals, repeated occurrences, `repeatable = true`, unsupported type/action combinations, unknown row fields (such as `nargs`), or otherwise invalid individual rows (except document-wide errors specified below and safety-limit failures in §6) MUST be labeled manual-only with a reason. Do not partially interpret that row. Other valid rows MAY remain typed. Missing/invalid IDs or alias lists, duplicate IDs, or aliases claimed by different rows invalidate the whole document because ownership is ambiguous. A syntactically valid but unsupported action such as `append` may retain its unique ID/aliases for diagnostics only. Mutually exclusive groups, paired boolean actions sharing a destination, subcommands, custom converters and multiple-value options have no typed semantics in schema 1 and MUST use manual handling; authors MUST NOT misdeclare them as independent scalar controls.

## 4. Exact argv contract

A consumer MUST maintain one ordered list of argument strings, independent of presentation groups. Opening, rescanning, changing source, saving/reloading or changing metadata MUST preserve existing tokens byte-for-byte in their UTF-8 representation and in the same order. Do not insert defaults, resolve aliases, deduplicate repeats, combine/split tokens, normalize numbers, expand variables or execute a shell. Only explicit user edits may change tokens; show the resulting exact argv before launch.

- Supported long `--name=value` splits at the first `=` only for presentation; preserve the original form on save. Separate `--name`, `value` and short `-n`, `value` forms remain separate. No inference for short attached values or bundles. Values may contain further `=` characters.
- A flag control means **emit this option**, not set the resulting scientific value. Enabled `store_true` emits only its alias (parser sets true); enabled `store_false` emits only its alias (parser sets false). Disabled emits nothing. Do not fabricate opposite flags, `false`, empty values or defaults. Required flags still need deliberate inclusion.
- Absence, a token with no following value, and an explicit empty string are distinct. For example `[]`, `["--label"]`, `["--label", ""]` and `["--label="]` MUST remain distinct representations. A supported string control can explicitly request an empty string; a blank manual value field MUST NOT silently add one. A missing value for a known scalar is a diagnostic, not authority to repair argv.
- Tokens after the first standalone `--` are manual positional content, even if they look like options. Unknown tokens, repetitions and ambiguous token/value pairings MUST stay manual and retain order. When pairing would consume a known option token as a value or has uncertain ownership, decline typed mapping; do not guess missing values. A negative numeric token matching the declared grammar may be a separate numeric value.
- On explicit edits to an unambiguous existing row, replace/remove only that row's identified token span in place. Newly enabled options MUST be inserted at a user-visible, confirmed position (default: immediately before `--`, otherwise at the end), without moving existing tokens. Use the first alias unless the user selects another; new long scalar options use `--name=value`, new short ones use two tokens. New flags use one token. Choice selection MUST preview the exact token text before acceptance, including any consumer-generated numeric spelling.

Metadata validation MAY prevent a typed edit from being accepted until corrected. It MUST NOT strand otherwise usable manual argv: offer explicit manual editing without metadata-based launch rejection, subject to the runner's independent safety/launch checks. The simulation may still reject those arguments. Never downgrade a known validation error silently or claim manual mode validates it.

## 5. Consistency and provenance

Authors MUST maintain declarations alongside source and bump the simulation source revision under their claimed SWSS versioning policy when changing this source-package metadata. `simulation_version` labels the revision the declaration describes; it is not an automatic version bump. Store declarations with captured source when used. Consumer writes to simulation files or automatic synchronization are not authorized by discovery.

Source manifests are optional: basic typed controls MUST work without them, with **binding unverified** shown. If `swss.source_files` is provided, consumers MUST hash the listed files as data and compare each entry before enabling typed use. A missing file, unsafe path or mismatched digest makes the binding stale/invalid and disables typed use. A declared version mismatch against a separately available, safely obtained simulation version also disables typed use; never import source to obtain it. Without hashes or a comparable version, display **binding unverified**, not **current**. Matching hashes prove only listed bytes match, not runtime semantics or completeness of a source package. Imported modules, dependencies and environment changes can invalidate behavior even with a matching entrypoint.

On rescan or before launch, recheck the whole companion-file bytes and any supplied bindings. Changes MUST invalidate the previous metadata-based preview, preserve argv and require review before reusing typed controls. A source change after the check remains possible; disclose the check's timing and do not claim isolation. Oversized source hashing is **binding unverified / manual-only**, not permission to skip a supplied binding and label it verified.

When declarations are used to configure a recorded run, consumers MUST retain the root-relative declaration path, exact companion-file bytes and SHA-256 (including application sections), portable schema version, declared simulation version, selected entrypoint, selected discovery source, binding status/reasons and checked source hashes (if any), plus the final exact argv. Runtime resolved parameters remain separate scientific provenance. If a declaration later becomes invalid or is bypassed, retain its last-used provenance and the bypass/review decision; a new manual run need not invent metadata. Do not record absolute workstation paths or credentials solely for this convention. Consumers must use their existing safe provenance storage; this proposal mandates no database schema or migration.

## 6. Safety and bounds

Discovery MUST parse data only: no imports, evaluation, `--help`, subprocesses, plugins, command interpolation, network fetches or dependency installation. Render descriptions as text. Declaration values do not authorize file writes or select executable code.

Proposed interoperable limits (exceeding any is a visible document failure with manual fallback). File bytes, depth, total entries and string bounds apply to the entire mixed-use file, including ignored application tables; parameter-specific limits apply within `swss`: **262,144 bytes** per document; nesting depth **8** (root table depth 1; each contained array/table adds 1); **4,096 total keys and array elements**; **128 parameter rows**; **8 aliases per row**; **100 choices per row**; **32 source files**; **4,096 UTF-8 bytes per string**, except **1,024 per path** and **128 per alias**. Strings MUST exclude NUL and control characters U+0000–U+001F/U+007F, except LF/tab in portable `help` and application text strings. Nonfinite numeric values invalidate the document. Within `swss`, dates/times and nested values outside specified structures invalidate portable metadata. Within application tables, TOML data types and nested tables/arrays are allowed within the whole-file bounds; portable consumers do not apply application schemas or dereference application paths. Scalar row type errors use the manual-row rule in §3; safety/count/string-limit failures invalidate the document.

Consumers MUST bound parsing work/memory as well as input bytes; reject excessive nesting before allocating unbounded structures (a bounded parser or isolated resource-limited parse is acceptable). Source hashing is streaming, limited to **16 MiB per file / 64 MiB total**. Consumers with tighter local limits MUST disclose them and fall back manually rather than claim full schema-1 support for all valid inputs. A source above the AST node limit can still use metadata because no AST is required; source exceeding hash limits cannot use a supplied verified binding in this revision. Manual argv remains available regardless of discovery failure, subject to independent runner safety constraints.

## 7. Illustrative valid declaration

This single `swss.toml` example combines portable parameters and an illustrative application capture section. It intentionally omits source hashes: its binding is unverified, but its typed controls remain usable. It is not a declaration for the real pilot and makes no claim about that solver's defaults. A real author must choose and validate the values against their parser.

```toml
[swss]
schema_version = 1
entrypoint = "simulate.py"
simulation_version = "0.1.1"

[[swss.parameters]]
id = "grid_size"
kind = "option"
options = ["--N", "-n"]
required = false
type = "integer"
action = "store"
help = "Grid resolution along each axis"
default = 192

[[swss.parameters]]
id = "timestep"
kind = "option"
options = ["--dt"]
required = true
type = "float"
action = "store"
help = "Integration timestep in model time units"

[[swss.parameters]]
id = "precision"
kind = "option"
options = ["--precision"]
required = false
type = "string"
action = "store"
help = "Arithmetic precision"
choices = ["single", "double"]
default = "double"

[[swss.parameters]]
id = "wavez"
kind = "option"
options = ["--wavez"]
required = false
type = "boolean"
action = "store_true"
help = "Write visualization output"
default = false

[[swss.parameters]]
id = "plots"
kind = "option"
options = ["--no-plots"]
required = false
type = "boolean"
action = "store_false"
help = "Disable plots"
default = true

[[swss.parameters]]
id = "label"
kind = "option"
options = ["--label"]
required = false
type = "string"
action = "store"
help = "Optional annotation"
default = ""

# Illustrative future application settings, not current SimShelf support.
[apps.simshelf.capture]
output_dir = "outputs"
max_file_mb = 25
max_run_mb = 200

[[apps.simshelf.capture.rules]]
pattern = "**/*.log"
action = "copy"

[[apps.simshelf.capture.rules]]
pattern = "**/*"
action = "reference"
```

A new tool-neutral simulation can use this same file with the `apps` tables omitted; no replacement or second file is needed. A third-party parameter reader extracts only `swss`. The example application keys illustrate where capture settings could move; their exact application schema and validation require separately reviewed SimShelf implementation work.

These rows correspond, respectively, to ordinary argparse declarations with `type=int`, `type=float, required=True`, `choices=["single", "double"]`, `action="store_true"`, `action="store_false"`, and `type=str`. The declared defaults must be supplied to the parser where applicable; the metadata does not supply them. No source code is executed to discover these rows. A declaration may describe another CLI implementation with the same behavior.

Malformed TOML example (duplicate portable key; reject whole document):

```toml
[swss]
schema_version = 1
schema_version = 2
```

Ambiguous example mutation: append a copy of `grid_size` with a new ID but the same `--N` alias; reject the entire document. Unsupported-row mutation: add `nargs = "+"` to `grid_size`; mark that entire row manual-only, keep other valid rows. Unsafe mutation: set `swss.entrypoint` to `"../outside.py"`; reject before reading that path. Unknown default: omit `default`; `default = null` is invalid TOML, while `default = "null"` is a literal string and invalid for a numeric row.

## 8. Proposed conformance fixtures

These are acceptance cases for a future consumer/reference validator, not claims of tests run against an implementation. Start with the complete example and a harmless matching entrypoint; mutations below specify the fixture input and required outcome.

| Fixture | Expected result |
| --- | --- |
| Valid mixed-use example; no argv | Six portable typed rows; application settings not used by discovery; hints only; no tokens inserted; missing required `--dt` diagnostic with manual escape; binding unverified. |
| Exact mixed argv: `["--N", "00192", "--dt=1e-3", "--label", "", "--unknown", "--", "--wavez"]` | Open/rescan/save/reload preserves every token; unknown and post-delimiter content manual; no trailing flag inferred. |
| `--label=a=b`, `--label=`, `--label` without value | First split only; explicit empty retained; missing value diagnosed without repair. |
| Enable each boolean flag independently; then disable | One exact option token per enabled flag, none when disabled; no flag value or opposite token. |
| Append positional `kind="positional", name="input", type="string", action="store"` with ID/help/required and no options | Manual label only; no fabricated position, name token or arity. |
| Repeated `--N`, `-n`; unknown option before apparent value | Preserve order/aliases; manual ambiguous ownership, no last-wins or duplicate removal. |
| `repeatable=true`, `action="append"`, or unknown row `nargs` | Manual-only affected rows, diagnostics; supported rows remain usable. |
| Duplicate key, duplicate ID/alias, bad header, schema 2 | Whole-document diagnostic; preserve argv, no silent metadata-source fallback. |
| Partial valid document omits `precision` | Remaining typed rows work; precision stays manual even if AST could find it. |
| `swss.toml` and unrelated metadata/static declarations disagree | Only SWSS file supplies portable declarations; no merge or automatic source switch; exact saved argv preserved. |
| `swss.toml` missing; another TOML exists | Missing-metadata diagnostic and manual fallback; no substitute file, recursive search or conversion. Application configuration requirements remain explicit. |
| New project with only Python and `swss.toml`, no `apps` tables | Portable discovery works with no application installation, manifest or second config file. |
| Complete SimShelf adoption with participating configurations | All affected launch/capture/discovery paths read `swss.toml`; validate new behavior before retiring old parsing or releasing. No generated compatibility files. |
| Historical run recorded before adoption | Records, snapshots, old config bytes, argv, artifacts and provenance remain unchanged and inspectable after reader retirement. No historical rewrite. |
| Unknown application namespace/version or application-semantic error | Portable fields still usable by other tools; application reports its own unsupported settings. No semantic interpretation of ignored tables. |
| Duplicate shared identity inside `apps.simshelf` conflicts with `swss` | SimShelf refuses conflicting app configuration; shared portable fields never overridden. |
| Valid portable section plus malformed/oversized/deep application section | Whole-file syntax/resource failure; ignoring app semantics does not bypass safety limits. |
| Modified companion bytes (including app-only edit), mismatched version, changed/missing hashed source | Invalidate preview and stale typed use, preserve argv/provenance; require review or explicit manual bypass. |
| Exact listed hashes; unlisted imported module changed | Binding says listed bytes match only; no semantic/conformance guarantee. |
| Source exceeds 20,000 AST nodes, metadata within limits | Metadata discovery requires no AST, imports or bound relaxation. Hash files within limits normally; oversized hashing falls back as specified. |
| Absolute/traversal/symlink/URI path or entrypoint mismatch | Refuse metadata association safely, preserve selected program and argv. |
| 262,145-byte file, depth 9, 129 rows, 9 aliases, 101 choices, 33 source entries, oversized strings/hash input | Enforce each stated limit and documented fallback; test exact allowed boundary too. |
| Invalid UTF-8, NUL, nonfinite float, date value in `swss` | Reject invalid portable metadata; a finite but wrong scalar type yields row fallback. No execution side effects. |
| Help or string value contains shell syntax | Display text, preserve explicit user argv as data; never evaluate it. |
| Declaration modified between safe open and preview/launch | Detect identity/byte change where checked; refuse reuse, disclose post-check race limit. |

Future conformance tests must assert no filesystem writes, imports, subprocesses or network activity during discovery, and verify provenance captures the exact declaration that informed user edits rather than a later file version.

## 9. Evidence, alternatives and owner decisions

Current SimShelf [parameter discovery documentation](https://github.com/mongstad/SimShelf/blob/fd603ff0dc98f7e093f274bcf0701bf092c6a60a/docs/PARAMETER_DISCOVERY.md) was checked at remote-main-matching commit `fd603ff0dc98f7e093f274bcf0701bf092c6a60a` on 2026-10-19. It documents a 20,000-node AST bound, a 256 KB discovery bound, explicit `simshelf-arguments.json` precedence, and manual fallback. [SimShelf #51](https://github.com/mongstad/SimShelf/issues/51) preserves exact argv through type-grouped presentation. **That existing JSON support is not support for this proposed TOML convention.** The reported v0.4.5 pilot failure is motivation from issue #16, not independently reproduced here. This describes the reviewed implementation as evidence, not a requirement to preserve JSON or legacy-file compatibility. This proposal does not lower safety bounds or rewrite the pilot.

The filename, single-file namespace architecture and absence of legacy compatibility are owner decisions already settled for this design. Remaining owner decisions before any normative amendment: approve SWSS 1.1 as the target, the detailed schema and manual-fallback rules, and source-binding/provenance costs and resource limits. The application schema and complete adoption implementation need separate review and validation. Optional future expansion (paired actions, subcommands, complete source manifests) needs a separately versioned review rather than guessing semantics in schema 1. Main risks include a partially converted application being released without complete validation, whole-file size limits rejecting unusually large application settings, and whole-file hashes requiring renewed review after app-only edits. Also relevant are stale author-maintained metadata, lexical differences across parsers, partial declarations that appear complete, and lack of sandboxing against source changes after checks. The explicit warnings, manual path and bounded bindings reduce these risks but cannot prove scientific behavior.

After design approval, a separate SimShelf issue may implement consumption and a separately authorized reference implementation may exercise these fixtures. No application implementation, checkpoint/pause design, license change, accepted-v1.0 edit or schema migration is included here.

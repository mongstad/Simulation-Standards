# Publication-readiness review

**2026-10-18 · Issue #8 · Owner review required.** The repository was verified **PRIVATE** during this review. Keep it private. This report does not authorize publication, merge, licensing, a release/tag or ratification. SWSS v1.0 remains a voluntary **draft**; no implementation is certified by this review.

## Evidence and readiness

The [single specification](../standards/SWSS/v1.0.md), [README](../README.md), [review gates](REVIEW.md) and [agent instructions](../AGENTS.md) retain independent Core / SimShelf / Wavez / Full profiles and owner-controlled decisions. Application contracts remain authoritative in their own repositories. No application or pilot was modified.

[Issue #6](https://github.com/mongstad/Simulation-Standards/issues/6) reports that the VB Vacuum Collapse Recirculator v0.4.3 pilot used `case_D.wvz`, exposing a repeat-run destination-collision risk. This is an owner-reported workflow observation, not an independently reproduced scientific result. The resulting naming requirements are documented; their presence does not prove the pilot satisfies them. No pilot data, run logs or numerical validation report is tracked here.

The [runtime gates](REVIEW.md) remain unchecked: scientific baseline and RNG preservation, automatic log capture, progress and metrics, failure/cancellation, concurrent outputs, WVZ1 numerical readback/viewer inspection, repeated captures/collision refusal and backup verification still need recorded evidence. No runtime tests were performed under issue #8. The proposed synthetic reference implementation remains future work; the reported external pilot does not establish that reference implementation or conformance.

## Licensing proposal — no grant made

These are alternatives for owner decision, not operative license terms. No LICENSE file, license header or definitive grant is added by this review.

| Candidate scope | Proposal and implications | Alternative / decision |
| --- | --- | --- |
| SWSS prose and documentation | **CC BY 4.0** would permit redistribution and adaptation, including commercial use, subject to attribution and other conditions. | Approve this scope explicitly, or retain the present unlicensed status while choosing different terms. |
| Future executable reference code | **MIT** would permit use, modification, redistribution, sublicensing and sale, with copyright and permission notices retained in copies or substantial portions; it includes warranty/liability disclaimers. | Approve only with an explicit file scope when code exists, or defer the code decision. No executable reference implementation is currently tracked. |

For CC BY 4.0, downstream sharing must retain supplied attribution/copyright/license/disclaimer information and a practicable source link, identify modifications, and provide the license text or link. Attribution must not imply endorsement; additional legal/technical restrictions cannot negate the granted rights. Compliant recipients retain the grant even if distribution later stops. Patent/trademark and some personal rights are outside that grant. See the official [CC BY deed](https://creativecommons.org/licenses/by/4.0/) and controlling [legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en).

The code proposal follows the [MIT text published by OSI](https://opensource.org/license/mit); it is a permissive software option, not a scientific warranty. Creative Commons [advises using software-specific licenses for software](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software), supporting a separate code scope.

Before adopting either proposal, the owner must approve:

1. Exact licenses, covered files, effective revision and whether any historical revisions are included; future code cannot be silently swept into a prose-only choice.
2. Copyright holder, year(s), attribution name/source URL and notice placement, with authority to license all included material.
3. Treatment of embedded TOML/command/API examples, future starter templates and mixed prose/code files. Their current license boundary is unresolved; a later explicit mapping or dual-license choice would need approval.
4. Exclusions for third-party material and separately owned application/pilot content. Linking to SimShelf or Wavez grants no rights to their code or documentation.

License permission to redistribute is separate from contribution intake, repository visibility and SWSS endorsement. None of those policies is changed here.

## Tracked-source and history audit

**Baseline:** `75659899e67f697e004ae16bc3aa8b2a5c6d90c7`, before this documentation change. After fetching/pruning origin, `main` and the assigned issue branch pointed to that commit; remote enumeration showed those two heads and no tags.

Coverage: all **5 tracked files**, **12 reachable commits**, **41 reachable Git objects**, and **12 distinct historical file blobs** across six historical paths, including the deleted `SWSS_v1.0_DRAFT.md`. Used `git ls-files`, `git rev-list --all`, `git rev-list --objects --all`, `git cat-file`, historical diffs and file review. Checked filenames, blob sizes/text encoding, commit metadata/messages, home-directory path patterns, email patterns, common token/private-key signatures and quoted secret assignments. Candidate reports omitted matched values. The proposed documentation was also checked before submission.

| Finding | Safe context / result | Owner action |
| --- | --- | --- |
| Identifying Git metadata | All 12 baseline commits contain author/committer email metadata; there are two distinct name/email identities, neither using GitHub's `users.noreply.github.com` domain. Examples: `958b7af`, `abe8ce5`, `7565989`. Addresses are deliberately not copied here. | Review locally and approve exposure of identities/history, or separately authorize remediation. Changing future Git identity would not remove past metadata. No history rewrite was performed. |
| Account and project identifiers | GitHub links identify the account in README-linked documents and the specification; the specification contains a vacuum-collapse example. Issue #6 names the external pilot, now summarized here and in README. | Confirm these identifiers and pilot attribution may be public, and that referenced resources will be accessible to intended readers. |
| Credentials and workstation paths | No credential-shaped values, private-key blocks, quoted secret assignments or absolute user-home paths were found in scanned blobs or commit text. | Treat as a bounded negative finding, not proof of absence of all secrets. |
| Secret files / research data / binaries | All historical file paths are Markdown. No tracked environment/credential files, research datasets, generated captures or binary blobs were found. Largest baseline blob: **18,670 bytes**, `standards/SWSS/v1.0.md` at `a207ddc` (blob `d2fb92e`). | No data deletion or size remediation identified within this scope. |
| Superseded draft | Root draft remains recoverable in history, introduced at `68f023d`, removed at `abe8ce5`. It is not a current second specification. | Accept historical draft exposure; do not treat it as the current contract. |

**Limits:** This is a bounded publication-content review, not an exhaustive security certification. Pattern checks can miss unfamiliar or encoded secrets. Coverage excludes unreachable/deleted remote objects, reflogs, untracked/ignored workstation files, other repositories, GitHub attachments, Actions artifacts, caches and server-only PR refs. Only the relevant issues were read; all issue/PR discussions and other hosted surfaces have not been privacy-audited. Those surfaces and any later commits need review before visibility changes. No history or data was deleted or rewritten.

## Quality checks and owner handoff

Checks passed for **21 relative links/anchors**, **15 GitHub file/tree targets**, fenced blocks, historical UTF-8 text and whitespace. Reviewed draft/profile terminology and documentation-only scope. The reference checkouts matched remote main: SimShelf `1aceecb3febf6e8e193fdc99d756ed345820d83c` and Wavez `681a46f8f8473ee6b5323ec4af71ada883183077`. Official licensing references were read on the review date. Technical references were checked against application Git objects; this verifies file targets, not anonymous-reader access after a future visibility change. Existing historical evidence remains historical; no runtime gates are marked complete.

Publication remains blocked pending owner decisions and evidence:

- Approve exact licensing scope and notices, then authorize their implementation separately.
- Resolve identifying metadata/project-name exposure and audit remaining hosted surfaces; approve any necessary remediation before it is attempted.
- Supply or explicitly disposition pending runtime evidence and permitted claims. An owner-authorized draft publication must still disclose untested behavior; ratification requires its separate gates.
- Review the final PR and any intervening changes, verify intended readers can access references, and recheck private visibility before a separately authorized visibility change.

The issue ends with a PR for review. It does not authorize another issue, public launch, tag/release, governance change or standard ratification.

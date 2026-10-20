# Agent instructions

This repository documents scientific simulation workflow conventions. These instructions apply to AI agents working here, alongside the owner's assigned issue.

## Scope and sources of truth

- SWSS is one independent, scientific workflow standard with a baseline and optional capabilities. No application-specific profiles, namespaces, APIs or formats belong in its portable requirements.
- The current specification text is `standards/SWSS/v2.0.md`, submitted for owner review. Earlier tracked versions are archival summaries; original text remains in Git history. Do not rewrite commit/tag history or external scientific records. Specification acceptance does not imply implemented consumers or certification.
- Propose and review portable additions to `swss.toml` or shared workflow contracts here first, then implement the accepted contract in adopting repositories with separate authorization. Consumer-specific details may remain local but cannot silently alter SWSS semantics. Developers may adopt or ignore SWSS.
- Keep normative requirements self-contained. External format/API documentation governs only the adapter or format selected by an implementation; it cannot silently change SWSS obligations.
- Avoid duplicating the entire specification in README, reviews or agent instructions. Keep links and terminology consistent.
- Never silently change scientific methods, numerical results, units, provenance or validation claims.

## Issue and branch workflow

- Work only within the assigned issue's scope. Use the existing issue-attached branch if one is provided. Otherwise create a dedicated branch from the appropriate base. Do not work directly on `main`.
- Preserve unrelated changes and existing history. Do not edit adopting application repositories or scientific simulations as part of a documentation issue.
- Prepare a pull request for owner review describing changes, checks, unresolved questions and important exclusions.
- **Do not merge, tag, release, publish or ratify a standard, change visibility/settings, or alter governance without explicit owner approval.**
- Do not add or modify license terms or contribution policies without explicit owner authorization.

## Quality and review

- Write concise, precise, testable requirements. Use MUST/SHOULD/MAY consistently and label drafts and proposals clearly.
- Prefer links to the applications' authoritative technical contracts over copied API or wire-format specifications.
- Check Markdown links and relative paths; review cross-document consistency and ensure no duplicate authoritative version is left behind when consolidation is in scope.
- Document actual validation evidence and limitations. Do not claim that tests, integrations or reference implementations have been exercised unless they have.
- Protect sensitive data; avoid committing generated binary captures, local environment files, machine-specific paths and run logs by default.
- Require no application installation for the baseline or portable metadata. Preserve independent capability boundaries.

The repository owner makes final scope, scientific, licensing, merge and publication decisions.

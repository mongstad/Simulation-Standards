# Agent instructions

This repository documents scientific simulation workflow conventions. These instructions apply to AI agents working here, alongside the owner's assigned issue.

## Scope and sources of truth

- SWSS is one independent, scientific workflow standard with a baseline and optional capabilities. Applications conform or adapt to SWSS; do not tailor the contract to a consuming application's architecture.
- Keep specifications, reference implementations, portable metadata, examples and their primary documentation application-independent. Do not introduce consumer product names, environment variables, APIs, capture policies, versions, implementation paths, installation requirements or repository links into these materials.
- Reference simulations must run independently and demonstrate the claimed SWSS requirements without requiring or detecting a named consumer. Consumer-specific adapters, integration tests and implementation notes belong in the respective consumer repository, under separate authorization.
- The current specification is `standards/SWSS/v2.0.md`. Earlier tracked versions are archival summaries; original text remains in Git history. Do not rewrite commit/tag history or external scientific records. Specification acceptance does not imply implemented consumers or certification.
- Propose and review portable additions to `swss.toml` or shared workflow contracts here first, then implement the accepted contract in adopting repositories with separate authorization. Consumer-local extensions do not authorize application-specific reference materials here or alter SWSS semantics.
- Keep normative requirements self-contained. Clearly label neutral transport examples as illustrative, not normative. Renaming a consumer protocol's variables does not make it a portable SWSS contract.
- Avoid duplicating the entire specification in README, reviews or agent instructions. Keep links and terminology consistent.
- Never silently change scientific methods, numerical results, units, provenance or validation claims.

## Issue and branch workflow

- Work only within the assigned issue's scope. Use the existing issue-attached branch if one is provided. Otherwise create a dedicated branch from the appropriate base. Do not work directly on `main`.
- Preserve unrelated changes and existing history. Do not edit adopting application repositories or scientific simulations as part of a documentation issue.
- Prepare a pull request for owner review describing changes, checks, unresolved questions and important exclusions.
- Owner review and approval occur before merge. Merging an approved PR completes that review; do not create additional issues, approval ceremonies or post-merge acceptance requirements for changes already reviewed and merged by the owner.
- Keep temporary review status, outstanding questions and implementation progress in issue or PR discussions, never in permanent repository documentation. Do not add statements such as "waiting for owner review," "pending owner approval" or "awaiting merge" to permanent documentation.
- **Do not merge, tag, release, publish, change visibility/settings, or alter governance without explicit owner approval.** A merge does not authorize a release or publication; those actions require separate owner approval.
- Do not add or modify license terms or contribution policies without explicit owner authorization.

## Quality and review

- Write concise, precise, testable requirements. Use MUST/SHOULD/MAY consistently and label drafts and proposals clearly.
- Review changed paths and content for named-consumer coupling, including optional adapters and tests. Use SWSS as the authority for portable behavior; keep consumer contract links and API or wire-format implementation guidance in the consumer repository.
- Check Markdown links and relative paths; review cross-document consistency and ensure no duplicate authoritative version is left behind when consolidation is in scope.
- Document actual validation evidence and limitations. Do not claim that tests, integrations or reference implementations have been exercised unless they have.
- Protect sensitive data; avoid committing generated binary captures, local environment files, machine-specific paths and run logs by default.
- Require no application installation for the baseline or portable metadata. Preserve independent capability boundaries.

The repository owner makes final scope, scientific, licensing, merge and publication decisions.

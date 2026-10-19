# Agent instructions

This repository documents voluntary scientific simulation workflow conventions. These instructions apply to AI agents working here, alongside the owner's assigned issue.

## Scope and sources of truth

- Keep the SWSS **Core** profile application-independent. SimShelf and Wavez are optional, separate integrations; never make either application depend on the other.
- The current normative SWSS specification is `standards/SWSS/v1.1.md`. Keep `v1.0.md` and past proposals/evidence unchanged as historical records. Specification acceptance does not imply implemented consumers, industry certification or scientific validation.
- SimShelf's own documentation and source govern its capture, progress, metrics and version behavior. Wavez's own documentation and source govern WVZ1, export, scene reading and visualization. Verify claims against current contracts; distinguish supported functionality, required configuration, proposed conventions and untested assumptions.
- Avoid duplicating the entire specification in README, reviews or agent instructions. Keep links and terminology consistent.
- Never silently change scientific methods, numerical results, units, provenance or validation claims.

## Issue and branch workflow

- Work only within the assigned issue's scope. Use the existing issue-attached branch if one is provided. Otherwise create a dedicated branch from the appropriate base. Do not work directly on `main`.
- Preserve unrelated changes and existing history. Do not edit the SimShelf or Wavez repositories as part of a Simulation-Standards documentation issue.
- Prepare a pull request for owner review describing changes, checks, unresolved questions and important exclusions.
- **Do not merge, tag, release, publish or ratify a standard, change visibility/settings, or alter governance without explicit owner approval.**
- Do not add or modify license terms or contribution policies without explicit owner authorization.

## Quality and review

- Write concise, precise, testable requirements. Use MUST/SHOULD/MAY consistently and label drafts and proposals clearly.
- Prefer links to the applications' authoritative technical contracts over copied API or wire-format specifications.
- Check Markdown links and relative paths; review cross-document consistency and ensure no duplicate authoritative version is left behind when consolidation is in scope.
- Document actual validation evidence and limitations. Do not claim that tests, integrations or reference implementations have been exercised unless they have.
- Protect sensitive data; avoid committing generated binary captures, local environment files, machine-specific paths and run logs by default.
- Make no assumptions that all users have both applications installed. Preserve the optional profile boundaries.

The repository owner makes final scope, scientific, licensing, merge and publication decisions.

# AI Software Delivery Framework

A reusable, project-independent framework for delivering software with AI agents (Claude Code) under
independent review and human control. Version **1.1.0**.

It gives a project: an engineering workflow (a 20-step vertical slice), ten agent definitions with
clear invocation rules, specialist **independent reviewers** (database, backend, frontend including
design conformance), independent QA and security, standard review reporting with severity rules,
configurable project profiles, and a forward-only way to adopt and upgrade it.

> The human is always the final decision authority. Agents are required to evaluate evidence rather than
> agree by default ("Independent Judgment — Evidence Over Agreement").

## Division of responsibility

ChatGPT (or another orchestrator) is the **Process Orchestrator**; Stitch (or the project's design tool) is
the **Primary UI/UX Designer**; Claude Code is the **Engineering Implementor**; specialist agents provide
**independent review and verification**.

## What is in this repository

| Path | Kind | Contents |
|---|---|---|
| `agents/` | **Canonical** | The 10 agents: `design`, `database-architect`, `backend`, `backend-reviewer`, `frontend`, `frontend-reviewer`, `reviewer`, `qa`, `security`, `devops` |
| `docs/POLICY.md` | **Canonical** | The policy (principles, DoR/DoD, risk, workflow, review standards, registry, practices) |
| `docs/PROJECT-CONFIGURATION.md` | **Canonical** | The split between canonical files and project configuration; what the project profile must say |
| `docs/VERSIONING.md` | **Canonical** | Version rule, history, compatibility, update procedure, rollback |
| `docs/ADOPTION.md` | **Canonical** | New-project bootstrap and existing-project adoption |
| `docs/VALIDATION.md` | **Canonical** | What has been validated, how, and what is *not* enforced or verified |
| `prompts/` | **Canonical** | Reusable prompts: bootstrap a new project, adopt in an existing project, upgrade |
| `templates/` | **Project-specific configuration** | Files each project copies and fills in: `CLAUDE.md`, project profile, adoption record, status log, coding standards, debt register, ADR, optional hook |
| `scripts/validate.py` | Tooling | Validator (Python standard library only) |
| `VERSION`, `CHANGELOG.md` | Release | Current version and history |

**Canonical** files are owned by the framework and are not edited inside a project (a project records a
*compatibility exception* instead). **Templates** become the project's own configuration and are never
overwritten by an upgrade.

## Quick start

- **New project:** follow `docs/ADOPTION.md` ("New-project bootstrap"), or give `prompts/bootstrap-new-project.md`
  to Claude Code inside the new project.
- **Existing project:** give `prompts/adopt-existing-project.md` to Claude Code inside that project. It
  adopts at a safe boundary, never interrupts work in progress, never reopens completed work, and records
  the adoption.
- **Upgrade:** `prompts/upgrade-framework.md` and `docs/VERSIONING.md`.

Choose the project's **criticality** (`PROTOTYPE` / `MVP` / `PRODUCTION` / `HIGH-CRITICALITY`) and
**readability** (`MID-LEVEL` / `SENIOR`) profiles with the human and record them in the project profile;
the framework never chooses them.

## Validate

```
python3 scripts/validate.py            # validate this repository
python3 scripts/validate.py --project /path/to/adopting-project   # check an adopting project's installed copy
```

## Honest limits

The review gates are **process rules carried by agent instructions and the project's `CLAUDE.md`**; nothing in
the framework blocks a commit automatically. The reviewer agents are read-only with respect to files by tool
allowlist (no write/edit tools) but keep shell access for inspection and running tests, which is restricted
by instruction only. See `docs/VALIDATION.md` for exactly what was verified and what was not.

## Releases

Tagged `vMAJOR.MINOR.PATCH`; the current release is `v1.1.0`. Migrating any particular project to a release
is a separate, deliberate step performed in that project.

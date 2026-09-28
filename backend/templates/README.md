# Zenflow Template Library

This directory contains reusable guideline templates for different agents and skills.

Purpose:
- keep agents/skills stable, stack-agnostic and tool-agnostic
- keep stack-specific behaviour in copyable guideline files
- adapt agents/skills contents to tool-specific syntax
- make repository bootstrapping predictable for new teams

## Folders
1. Agents

These templates will be initialized as either Agents for Copilot or Skills for Claude/Open Code.

In general there is no need to change these files, as they determine primarily the workflow and will redirect the tool to refer to the guideline files (next section) for the rules that the agent/skill should follow.

`agents/tech-migration.md.j2` adapts the planning-only Tech Migration workflow.
It is self-contained: project instructions and installed stack guidelines are
optional context, not required companion files. Copilot can render it as either
`.github/agents/tech-migration.agent.md` or
`.github/skills/tech-migration/SKILL.md`; OpenCode and Claude Code render it as
`skills/tech-migration/SKILL.md` in their own tool directories. The selected
setup stack is the current-project context, not an automatic target stack.
Migration plans default to `docs/plans/[migration-slug].md`; G0-G7 describe
later evidence and approvals, not work the planner executes. The Orchestrator
can use an installed Tech Migration agent/skill for migration requests and
stops after plan review. Select Tech Migration separately when exporting only
selected workflows.

2. Guidelines

Based on the stack chosen by the user when running the init command, the relevant files will be copied to:
* `.github/guidelines` for Copilot
* each skill's `references` folder for Claude/Open Code

Guideline logic:
- **architecture-backend.md**: Backend framework conventions, package structure, patterns, validation rules, database expectations, and testing strategy.
- **architecture-frontend.md**: Frontend framework conventions, component structure, API client patterns, routing, styling, accessibility, and testing strategy.
- **review-backend.md** and **review-frontend.md**: Review scope and audit checklist against the architecture guidelines. They reference the above two architecture documents to review what is implemented and do not contain substantive stack related rules.
- **conventions.md** (optional): Git branch and commit conventions.

The more explicit these files are, the more consistently all tools can follow your standards.

These are the files to be edited with the architectural guidelines your team agrees on.

To configure additional languages or frameworks, similar files to the existing ones have to be added to `guidelines` folder, and the new options and paths updated in the constants in `src/zenflow/stack.py` for the initialisation tool to work.

3. Instructions

This is only used by Copilot to configure how questions are asked to the user and does not need to be customised.

4. Partials

Partial templates are shared across different stacks and involve formatting of output, checklists, and handover. You can define your own partials that can be loaded automatically by the init script into the actual agents/skills templates. See files in `guidelines/backend/` for an example at the end of each file.

## Jinja Templates

**Agent and guideline source files** are [Jinja2](https://jinja.palletsprojects.com/) templates (`.md.j2`). At init time, each template will be rendered with a tool-specific context, and assembled files will be written to the target.

For agent source files, each tool gets its own `guidelines` context so file references resolve to the correct location:

| Variable | Copilot | OpenCode | Claude Code |
|---|---|---|---|
| `{{ guidelines.backend_arch }}` | `.github/guidelines/architecture-backend.md` | `.opencode/skills/backend/references/architecture.md` | `.claude/skills/backend/references/architecture.md` |
| `{{ guidelines.review_backend }}` | `.github/guidelines/review-backend.md` | `.opencode/skills/reviewer/references/review-backend.md` | `.claude/skills/reviewer/references/review-backend.md` |
| `{{ guidelines.conventions }}` | `.github/guidelines/conventions.md` | `.opencode/skills/git/references/conventions.md` | `.claude/skills/git/references/conventions.md` |

**Partials** will be included in source files using standard Jinja2 syntax:

```
{% include 'partials/backend-handover.md.j2' %}
```

The entire templates folder is provided to the Jinja2 environment when rendering the files, so any filepath within templates can be referenced directly.

Other partials can be included similarly according to the team's needs. 

## Notes

- Keep template files generic enough to reuse across projects.
- After cloning into a project for use, modify files in `.github/guidelines` or `skills/<skill name>/references` as necessary for the project's requirements.

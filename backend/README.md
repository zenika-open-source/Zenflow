# Zenflow

Zenflow is an **open-source project** that showcases the most common agentic workflows for AI-driven software development. Each workflow is implemented as a team of collaborating agents or skills, demonstrating patterns that teams can study, adapt, and build upon.

**Zenflow supports GitHub Copilot (VS Code), OpenCode, and Claude Code.** Each tool is optional — you can install any combination.

## Quick Start

To install a boilerplate version of Zenflow in an existing repository, install dependencies with [Python](https://www.python.org/) and [uv](https://docs.astral.sh/uv/) and run the init script:

```bash
uv sync
uv run zenflow-init
```

! WARNING ! If you have existing configurations for your tools configured locally in your project directory, files with the same name will be overloaded when running this script.

Follow the prompts to:
1. Enter the target project directory.
2. Choose which tools to set up (GitHub Copilot, OpenCode, Claude Code).
3. Choose backend stack (Java/Spring Boot, Go/Gin, Python/FastAPI).
4. Choose frontend stack (React, Next.js App Router).
5. Optionally include git conventions.

### What the script installs
After running the script, the target repository will have:

- **.github/skills/**, **.github/instructions/** (if GitHub Copilot selected)
- **.opencode/skills/** (if OpenCode selected)
- **.claude/skills/** (if Claude Code selected)

### Recommended Supporting Files
For best results, ensure the target project provides additional context:

- **README.md**: The Documentation agent updates the README, so it helps if the project already has a clear structure and an API or usage section to extend.
- **docs/plans/**: The Backend and Frontend agents/skills save planning artifacts here for user review before implementation. Create this directory up front to keep outputs consistent.
- **.github/copilot-instructions.md**, **AGENTS.md** or **CLAUDE.md** (depending on tool used): Useful for project-specific context, terminology, and documentation expectations. The Documentation agent/skill will load this if available.

## Workflows

### 1. Fullstack Application — New Feature

This workflow delivers a complete feature end-to-end, from branch creation to a merged pull request. 

* When using GitHub Copilot, a top-level **Orchestrator** agent breaks the feature request into tasks, delegating each one to a specialist sub-agent in sequence. Subagents can also be loaded directly if preferable.
* When using OpenCode or ClaudeCode, each agent is loaded as a Skill instead. The **Orchestrator** skill can be invoked and it will delegate subtasks to specific skills. Each skill can also be invoked directly.

| Step | Agent | Responsibility |
|------|-------|----------------|
| 0 | Git | Creates and checks out a feature branch |
| 1 | Backend | Produces feature plan (saved to `docs/plans/`) for user approval |
| 2 | Backend | Implements API endpoints and business logic |
| 3 | Frontend | Produces frontend plan for user approval |
| 4 | Frontend | Builds UI components and wires up API calls |
| 5 | Reviewer | Performs security and quality review |
| 6 | Documentation | Updates README and other documentation where applicable. |
| 7 | Git | Stages changes, writes a conventional commit, and prepares a PR description |

For a detailed flow diagram, see [docs/diagrams/fullstack-newfeature.md](docs/diagrams/fullstack-newfeature.md).

## Extending and Customising Zenflow

To extend Zenflow with team specific guidelines for your own use:
1. Fork the repository
2. Update the templates with additional guidelines, or include other templates
3. Team members cloning from your repository will be able to bootstrap their tools with team specific guidelines.

Zenflow includes a stack template library under `templates/`.

See [templates/README.md](templates/README.md) for available templates and structure, as well as how to extend this for your own use.

After customizing, you can run `uv run zenflow-init` again to install the new workflow.

## Project Structure

```
Zenflow/
├── docs/             # Explanation of Zenflow orchestration
├── src/              # Setup script (Jinja2-based rendering)
├── templates/        # Reusable templates
```


## License

This project is licensed under the [Apache License 2.0](LICENSE).

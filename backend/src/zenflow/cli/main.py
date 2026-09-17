"""CLI entry point and interactive wizard for Zenflow initialization."""

from __future__ import annotations

import argparse
import os
import sys

from zenflow.core.errors import ZenflowError
from zenflow.core.models import DeploymentResult, GuidelineSelection, ToolSelection
from zenflow.core.service import get_dirs, init_project, validate_dirs
from zenflow.core.service import repo_root as get_repo_root
from zenflow.core.stack import BACKEND, FRONTEND

# ---------------------------------------------------------------------------
# Stack selection
# ---------------------------------------------------------------------------


def _choose_stack(label: str, options: list[tuple[str, str, str]]) -> tuple[str, str, str]:
    """Prompt user to choose a stack from a numbered list.

    Args:
        label: Human-readable name for the stack type (e.g. 'backend').
        options: List of (label, arch_filename, doc_filename) entries.

    Returns:
        The chosen (label, arch_filename, doc_filename) tuple.
    """
    print()
    print(f"Choose {label}:")
    for i, (name, _, _) in enumerate(options, start=1):
        print(f"  {i}) {name}")
    choice = input(f"Enter choice [1-{len(options)}]: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(options):
        print(f"Error: invalid {label} choice '{choice}'.", file=sys.stderr)
        sys.exit(1)
    return options[int(choice) - 1]


def _choose_language_then_framework(
    domain: str,
    stacks: dict[str, list[tuple[str, str, str]]],
) -> tuple[str, str]:
    """Prompt user to choose a language then a framework.

    Args:
        domain: Human-readable domain name (e.g. 'backend').
        stacks: Dict of language label to list of (label, arch_file, doc_file) framework entries.

    Returns:
        Tuple of (arch_filename, doc_filename).
    """
    languages = [(lang, lang, "") for lang in stacks]
    _, language, _ = _choose_stack(f"{domain} language", languages)
    _, arch_file, doc_file = _choose_stack(f"{domain} framework", stacks[language])
    return arch_file, doc_file


# ---------------------------------------------------------------------------
# User prompts
# ---------------------------------------------------------------------------


def _prompt_tool_selection() -> ToolSelection:
    """Prompt user to select which AI tools to set up.

    Returns:
        ToolSelection with the user's choices.
    """
    return ToolSelection(
        copilot=input("Set up GitHub Copilot (VS Code)? [Y/N]: ").strip().lower() == "y",
        opencode=input("Set up OpenCode? [Y/N]: ").strip().lower() == "y",
        claude=input("Set up Claude Code? [Y/N]: ").strip().lower() == "y",
    )


def _prompt_guideline_selection() -> GuidelineSelection:
    """Prompt user to select backend, frontend, and conventions guidelines.

    Returns:
        GuidelineSelection with the user's file choices.
    """
    include_backend = input("Include backend guidelines? [Y/N]: ").strip().lower() == "y"
    include_frontend = input("Include frontend guidelines? [Y/N]: ").strip().lower() == "y"

    backend_arch_file, backend_doc_file = (
        _choose_language_then_framework("backend", BACKEND) if include_backend else ("", "")
    )
    frontend_arch_file, frontend_doc_file = (
        _choose_language_then_framework("frontend", FRONTEND) if include_frontend else ("", "")
    )

    print()
    include_conventions = input("Include git conventions template? [Y/N]: ").strip().lower() != "n"

    return GuidelineSelection(
        backend_arch_file=backend_arch_file,
        backend_doc_file=backend_doc_file,
        frontend_arch_file=frontend_arch_file,
        frontend_doc_file=frontend_doc_file,
        include_conventions=include_conventions,
    )


def _print_plan(target_path: str, tools: ToolSelection) -> None:
    """Print a summary of what will be generated before deployment.

    Args:
        target_path: Resolved target directory path.
        tools: Selected AI tools.
    """
    print("Zenflow initialization")
    print(f"Target path: {target_path}")
    print("Tools:")
    if tools.copilot:
        print("  ✓ GitHub Copilot (VS Code)")
    if tools.opencode:
        print("  ✓ OpenCode")
    if tools.claude:
        print("  ✓ Claude Code")
    print()
    print("The following will be generated:")
    if tools.copilot:
        print("  - .github/skills/        (Copilot skill definitions + references/)")
        print("  - .github/instructions/  (instruction files)")
    if tools.opencode:
        print("  - .opencode/skills/      (OpenCode skill definitions + references/)")
    if tools.claude:
        print("  - .claude/skills/        (Claude Code skill definitions + references/)")
    print()
    input("Press any key to continue...")
    print()


def _print_summary(result: DeploymentResult) -> None:
    """Print post-deployment summary.

    Args:
        result: Outcome returned by init_project.
    """
    guidelines = result.guidelines
    backend_doc_msg: str | None = (
        "Included backend documentation template"
        if guidelines.backend_doc_file
        else ("Skipped backend documentation template" if guidelines.include_backend else None)
    )
    frontend_doc_msg: str | None = (
        "Included frontend documentation template"
        if guidelines.frontend_doc_file
        else ("Skipped frontend documentation template" if guidelines.include_frontend else None)
    )
    conventions_msg = "Included conventions" if guidelines.include_conventions else "Skipped conventions"

    print()
    print("Initialization complete.")
    print(f"Target: {result.target_path}")
    if "copilot" in result.deployed:
        print("✓ GitHub Copilot (VS Code): .github/skills/ (with references/) and instructions")
    if "opencode" in result.deployed:
        print("✓ OpenCode: .opencode/skills/ (with references/)")
    if "claude" in result.deployed:
        print("✓ Claude Code: .claude/skills/ (with references/)")
    if backend_doc_msg:
        print(f"- {backend_doc_msg}")
    if frontend_doc_msg:
        print(f"- {frontend_doc_msg}")
    print(f"- {conventions_msg}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Zenflow initialization wizard."""
    parser = argparse.ArgumentParser(
        prog="zenflow-init",
        description="Initializes Zenflow scaffolding in a target directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()

    repo_root = get_repo_root()

    src = get_dirs(repo_root)
    try:
        validate_dirs(src.agents, src.instructions, src.guidelines)
    except ZenflowError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    default_target_path = os.path.join(repo_root, "target")
    target_path_input = input(f"Target path [{default_target_path}]: ").strip()
    target_path = target_path_input or default_target_path

    tools = _prompt_tool_selection()
    if not tools.any_selected():
        print("Error: at least one tool must be selected.", file=sys.stderr)
        sys.exit(1)

    _print_plan(target_path, tools)

    guidelines = _prompt_guideline_selection()

    print()
    print("Deploying selected tools...")
    try:
        result = init_project(repo_root, target_path, tools, guidelines)
    except ZenflowError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    _print_summary(result)


if __name__ == "__main__":
    main()

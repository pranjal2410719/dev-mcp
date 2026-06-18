"""
MCP prompt templates for dev-mcp.

Provides prebuilt prompt templates that inject project context and
guide AI assistants through common workflows.
"""

from __future__ import annotations

from app import mcp, load_context as get_context


@mcp.prompt(
    name="project-overview",
    description="A complete project overview prompt that injects the full project context for AI assistants.",
)
def project_overview_prompt(path: str = ".") -> str:
    """Generate a project overview prompt from the current context.

    Args:
        path: Project root directory.
    """
    ctx = get_context(path)
    md = ctx.to_markdown()

    return (
        "# Project Overview\n\n"
        "You are working on the following project. Read the context carefully "
        "before making any changes.\n\n"
        f"{md}\n\n"
        "## Instructions\n\n"
        "1. Understand the tech stack before suggesting solutions.\n"
        "2. Follow the project's code conventions.\n"
        "3. Check active tasks to avoid duplicating work.\n"
        "4. Log important decisions using the `add_decision` tool.\n"
        "5. Update task status as you make progress."
    )


@mcp.prompt(
    name="code-review",
    description="Code review guidelines specific to this project's conventions and tech stack.",
)
def code_review_prompt(path: str = ".") -> str:
    """Generate a code review prompt using project conventions.

    Args:
        path: Project root directory.
    """
    ctx = get_context(path)
    conventions = ctx.data.get("conventions", {})

    guidelines = []
    if conventions.get("code_style"):
        guidelines.append(f"- Code style: {conventions['code_style']}")
    if conventions.get("testing_approach"):
        guidelines.append(f"- Testing: {conventions['testing_approach']}")
    if conventions.get("naming_conventions"):
        guidelines.append(f"- Naming: {conventions['naming_conventions']}")

    tech = ctx.data.get("tech_stack", {})
    stack_info = []
    for category, items in tech.items():
        if items:
            stack_info.append(f"- {category.replace('_', ' ').title()}: {', '.join(items)}")

    stack_section = "\n".join(stack_info) if stack_info else "N/A"
    guidelines_section = "\n".join(guidelines) if guidelines else "No conventions defined yet."

    return (
        "# Code Review Guidelines\n\n"
        "## Tech Stack\n"
        f"{stack_section}\n\n"
        "## Project Conventions\n"
        f"{guidelines_section}\n\n"
        "## Review Checklist\n\n"
        "1. Does the code follow the project's established patterns?\n"
        "2. Are there existing tests? If so, do they still pass?\n"
        "3. Are error cases handled properly?\n"
        "4. Is the code idiomatic for the project's language/framework?\n"
        "5. Are there any security concerns?\n"
        "6. Does this change respect the architecture decisions?\n\n"
        "Run `git_diff` to see the changes being reviewed."
    )


@mcp.prompt(
    name="architectural-decision",
    description="Template for recording an Architecture Decision Record (ADR).",
)
def architecture_decision_prompt() -> str:
    """Prompt template for creating an ADR."""
    return (
        "# Architecture Decision Record\n\n"
        "## Title\n\n"
        "[Short title of the decision]\n\n"
        "## Context\n\n"
        "[What is the problem or motivation? What constraints exist?]\n\n"
        "## Decision\n\n"
        "[What was decided? Be specific.]\n\n"
        "## Rationale\n\n"
        "[Why was this the best choice? What trade-offs were considered?]\n\n"
        "## Alternatives Considered\n\n"
        "- [Alternative 1]: [Why it was not chosen]\n"
        "- [Alternative 2]: [Why it was not chosen]\n\n"
        "## Consequences\n\n"
        "[What becomes easier or harder as a result?]\n\n"
        "---\n"
        "Use the `add_decision` tool to log this in the project context."
    )


@mcp.prompt(
    name="feature-plan",
    description="Template for planning a new feature with tasks, branch strategy, and milestones.",
)
def feature_plan_prompt() -> str:
    """Prompt template for planning a new feature."""
    return (
        "# Feature Plan\n\n"
        "## Overview\n\n"
        "- **Feature name:**\n"
        "- **Goal:**\n"
        "- **Success criteria:**\n\n"
        "## Implementation Steps\n\n"
        "1. [Step 1]\n"
        "2. [Step 2]\n"
        "3. [Step 3]\n\n"
        "## Files to Modify\n\n"
        "- [File 1]: [What to change]\n"
        "- [File 2]: [What to change]\n\n"
        "## Testing Strategy\n\n"
        "[How will this be tested?]\n\n"
        "---\n"
        "After planning, register tasks using the `add_task` tool."
    )

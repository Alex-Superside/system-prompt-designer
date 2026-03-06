"""Command-line interface for the prompt design system.

Commands
--------
init-spec   Scaffold a blank agent spec Markdown file.
design      Parse a spec, select a tier, (optionally) call OpenAI to enrich the
            Task Block, and render a system prompt.
evaluate    Run a saved design against structured evaluation scenarios.
audit       Audit a saved design for linguistic noise and orthogonality leaks.
refine      Load a saved design, apply user feedback via the LLM, and overwrite.
run         Load a saved system prompt and test it against a user message.

The ``design`` and ``refine`` commands wire an OpenAIProvider by default when
OPENAI_API_KEY is present in the environment.  Pass ``--no-llm`` to force
heuristic-only mode, or ``--verbose`` to print the exact prompt sent to OpenAI.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from dotenv import load_dotenv
from rich.console import Console

if TYPE_CHECKING:
    from .providers import OpenAIProvider


def _load_env() -> None:
    """Load .env and .env.local from cwd so OPENAI_API_KEY is available without exporting.

    Load order (later wins):
    1. .env          — shared defaults, override=False so existing env vars are preserved
    2. .env.local    — local developer overrides, override=True so it wins over .env values
    """
    cwd = Path.cwd()
    load_dotenv(cwd / ".env", override=False)
    load_dotenv(cwd / ".env.local", override=True)  # local overrides; add to .gitignore


# Load env as soon as the CLI module is imported (e.g. when running `promptctl`).
_load_env()

from .agents import DesignAgent, EvaluatorAgent, LinguisticAuditorAgent
from .config import AppConfig, LLMConfig, VerbosityLevel
from .models import (
    EvaluationReport,
    EvaluationScenario,
    LinguisticAuditReport,
    PromptDesign,
    PromptTier,
)
from .patterns import PatternSelector
from .providers import UsageMetadata
from .prompt_templates import load_template
from .rule_blocks import RuleBlockRegistry
from .spec_parser import parse_agent_spec_from_markdown
from .storage import ProjectStorage

app = typer.Typer(help="Prompt design system CLI.")
console = Console()

FEEDBACK_PREVIEW_LENGTH = 60


@app.command("init-spec")
def init_spec(
    identifier: str = typer.Argument(..., help="Identifier for the new agent."),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the spec Markdown file.",
    ),
) -> None:
    """Create a minimal Markdown skeleton for an agent specification."""
    config = AppConfig.from_cwd()
    filename = output or Path(f"{identifier}.agent-spec.md")

    if filename.exists():
        console.print(f"[red]Refusing to overwrite existing spec file:[/red] {filename}")
        raise typer.Exit(code=1)

    lines = [
        f"# Agent Spec: {identifier}",
        "",
        "## Summary",
        "",
        "- Short description of the agent's purpose.",
        "",
        "## Role",
        "",
        "- Narrative description of the agent's role.",
        "",
        "## Inputs",
        "",
        "- What the agent receives (user messages, documents, context).",
        "",
        "## Outputs",
        "",
        "- What the agent must produce.",
        "",
        "## Constraints",
        "",
        "- Global constraints, must-not rules, guardrails.",
        "",
    ]

    filename.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]Created agent spec template at[/green] {filename}")
    console.print(f"Project root: {config.paths.root_dir}")


@app.command("design")
def design(
    spec_path: Path = typer.Argument(..., help="Path to the agent spec Markdown file."),
    tier: PromptTier = typer.Option(
        PromptTier.TIER_2,
        "--tier",
        "-t",
        case_sensitive=False,
        help="Prompt tier to prefer when auto-tier is disabled.",
    ),
    auto_tier: bool = typer.Option(
        True,
        "--auto-tier/--no-auto-tier",
        help="Automatically select prompt tier based on the spec.",
    ),
    use_llm: bool = typer.Option(
        True,
        "--llm/--no-llm",
        help=(
            "Call OpenAI to enrich the Task Block.  Reads OPENAI_API_KEY from "
            "the environment.  Falls back to heuristic-only when the key is absent."
        ),
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print the prompt sent to OpenAI before calling the API.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use (gpt-5.4, gpt-5.4-pro, gpt-5-mini, gpt-4o).",
    ),
    verbosity: str | None = typer.Option(
        None,
        "--verbosity",
        "-vb",
        help="Reasoning effort level (low, medium, high) for gpt-5.x models.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the rendered system prompt.",
    ),
) -> None:
    """Create a prompt design from a spec and render its system prompt.

    When OPENAI_API_KEY is set and ``--no-llm`` is not passed, OpenAI is called
    to enrich the heuristic scaffold with a substantive goal, acceptance
    criteria, constraints, and (for Tier 2+) execution steps tailored to the
    agent being designed.
    """
    if not spec_path.exists():
        console.print(f"[red]Spec file not found: {spec_path}[/red]")
        raise typer.Exit(code=1)

    config = AppConfig.from_cwd()
    registry = RuleBlockRegistry.from_config(config)
    storage = ProjectStorage(config)

    agent_spec = parse_agent_spec_from_markdown(spec_path)

    # Parse and validate verbosity if provided
    verbosity_level: VerbosityLevel | None = None
    if verbosity:
        try:
            verbosity_level = VerbosityLevel(verbosity)
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid verbosity level '{verbosity}'. "
                f"Must be one of: low, medium, high"
            )
            raise typer.Exit(code=1)

    llm_client = _resolve_llm_client(
        use_llm=use_llm, verbose=verbose, model=model, verbosity=verbosity_level
    )
    if use_llm and llm_client is None:
        console.print(
            "[yellow bold]USING ORTHOGONAL FRAMEWORK (HEURISTIC MODE)[/yellow bold]"
        )
        console.print("To enable LLM enrichment, set OPENAI_API_KEY.")
        console.print()

    template_loader = lambda name: load_template(config.paths, name)

    selector = PatternSelector()
    design_agent = DesignAgent(
        pattern_selector=selector,
        rule_block_registry=registry,
        llm_client=llm_client,
        verbose=verbose,
        template_loader=template_loader,
    )

    explicit_tier_value: str | None = None if auto_tier else tier.value

    design_model = design_agent.create_design(
        agent_spec=agent_spec,
        explicit_tier=explicit_tier_value,
    )

    storage.copy_spec_into_project(spec_path, agent_spec.identifier)
    design_path = storage.save_design(design_model, overwrite=True)

    rendered = _render_prompt(design_model)

    if output is not None:
        prompt_path = storage.save_rendered_prompt(
            design=design_model,
            rendered_prompt=rendered,
            overwrite=True,
            filename=output,
        )
        console.print(f"[green]Wrote system prompt to[/green] {prompt_path}")
    else:
        prompt_path = storage.save_rendered_prompt(
            design=design_model,
            rendered_prompt=rendered,
            overwrite=True,
        )
        console.rule("Rendered System Prompt (preview)")
        console.print(rendered)

    console.print(f"[green]Saved design[/green] to {design_path}")
    console.print(f"[green]Saved prompt[/green] to {prompt_path}")


@app.command("evaluate")
def evaluate(
    identifier: str = typer.Argument(..., help="Project identifier (matches spec identifier)."),
    scenarios_path: Path = typer.Argument(
        ...,
        help="Path to a JSON file containing evaluation scenarios.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the evaluation report JSON.",
    ),
) -> None:
    """Evaluate a saved design against structured scenarios."""
    if not scenarios_path.exists():
        console.print(f"[red]Scenarios file not found:[/red] {scenarios_path}")
        raise typer.Exit(code=1)

    config = AppConfig.from_cwd()
    storage = ProjectStorage(config)
    registry = RuleBlockRegistry.from_config(config)

    try:
        design_model = storage.load_design(identifier)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    scenarios = _load_scenarios(scenarios_path)
    evaluator = EvaluatorAgent(llm_client=None, rule_block_registry=registry)
    report = evaluator.evaluate(design_model, scenarios)

    _print_report(report)

    if output is not None:
        output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[green]Saved evaluation report to[/green] {output}")


@app.command("refine")
def refine(
    identifier: str = typer.Argument(..., help="Project identifier to refine."),
    feedback: str = typer.Option(
        ...,
        "--feedback",
        "-f",
        help="Plain-text feedback describing what to change in the design.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print the refinement prompt sent to OpenAI.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use (gpt-5.4, gpt-5.4-pro, gpt-5-mini, gpt-4o).",
    ),
    verbosity: str | None = typer.Option(
        None,
        "--verbosity",
        "-vb",
        help="Reasoning effort level (low, medium, high) for gpt-5.x models.",
    ),
) -> None:
    """Revise a saved design based on feedback and re-render its system prompt.

    Loads the existing design for *identifier*, sends it along with *feedback*
    to the LLM, and overwrites both the design JSON and the rendered system
    prompt with the revised version.
    """
    if not feedback.strip():
        console.print("[yellow]Warning:[/yellow] Feedback is empty — nothing to refine.")
        raise typer.Exit(code=1)

    config = AppConfig.from_cwd()
    registry = RuleBlockRegistry.from_config(config)
    storage = ProjectStorage(config)

    try:
        design_model = storage.load_design(identifier)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print(
            f"[dim]Run 'promptctl design <spec>' first to create a design for '{identifier}'.[/dim]"
        )
        raise typer.Exit(code=1) from exc

    # Parse and validate verbosity if provided
    verbosity_level: VerbosityLevel | None = None
    if verbosity:
        try:
            verbosity_level = VerbosityLevel(verbosity)
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid verbosity level '{verbosity}'. "
                f"Must be one of: low, medium, high"
            )
            raise typer.Exit(code=1)

    llm_client = _resolve_llm_client(
        use_llm=True, verbose=verbose, model=model, verbosity=verbosity_level
    )
    if llm_client is None:
        console.print(
            "[red]Error:[/red] A working LLM client is required for refinement. "
            "Set OPENAI_API_KEY and ensure the 'openai' package is installed."
        )
        raise typer.Exit(code=1)

    template_loader = lambda name: load_template(config.paths, name)
    selector = PatternSelector()
    design_agent = DesignAgent(
        pattern_selector=selector,
        rule_block_registry=registry,
        llm_client=llm_client,
        verbose=verbose,
        template_loader=template_loader,
    )

    refined = design_agent.refine_design(design_model, feedback)

    design_path = storage.save_design(refined, overwrite=True)
    rendered = _render_prompt(refined)
    prompt_path = storage.save_rendered_prompt(refined, rendered, overwrite=True)

    truncated = (
        feedback[:FEEDBACK_PREVIEW_LENGTH] + "..."
        if len(feedback) > FEEDBACK_PREVIEW_LENGTH
        else feedback
    )
    console.print(f'[green]✓[/green] Refined design based on feedback: "{truncated}"')
    console.print(f"[green]✓[/green] Saved design to {design_path}")
    console.print(f"[green]✓[/green] Rendered prompt to {prompt_path}")


@app.command("audit")
def audit(
    identifier: str = typer.Argument(..., help="Project identifier to audit."),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print the audit prompt sent to OpenAI.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use (gpt-5.4, gpt-5.4-pro, gpt-5-mini, gpt-4o).",
    ),
    verbosity: str | None = typer.Option(
        None,
        "--verbosity",
        "-vb",
        help="Reasoning effort level (low, medium, high) for gpt-5.x models.",
    ),
) -> None:
    """Audit a saved design for linguistic noise and orthogonality leaks."""
    config = AppConfig.from_cwd()
    storage = ProjectStorage(config)

    try:
        design_model = storage.load_design(identifier)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    # Parse and validate verbosity if provided
    verbosity_level: VerbosityLevel | None = None
    if verbosity:
        try:
            verbosity_level = VerbosityLevel(verbosity)
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid verbosity level '{verbosity}'. "
                f"Must be one of: low, medium, high"
            )
            raise typer.Exit(code=1)

    llm_client = _resolve_llm_client(
        use_llm=True, verbose=verbose, model=model, verbosity=verbosity_level
    )
    if llm_client is None:
        console.print(
            "[red]Error:[/red] A working LLM client is required for auditing. "
            "Set OPENAI_API_KEY and ensure the 'openai' package is installed."
        )
        raise typer.Exit(code=1)

    template_loader = lambda name: load_template(config.paths, name)
    auditor = LinguisticAuditorAgent(
        llm_client=llm_client,
        verbose=verbose,
        template_loader=template_loader,
    )
    report = auditor.audit_design(design_model)

    _print_audit_report(report)


@app.command("run")
def run(
    identifier: str = typer.Argument(..., help="Project identifier to test."),
    message: str = typer.Option(
        ...,
        "--message",
        help="User message to send against the saved system prompt.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use (gpt-5.4, gpt-5.4-pro, gpt-5-mini, gpt-4o).",
    ),
    verbosity: str | None = typer.Option(
        None,
        "--verbosity",
        "-vb",
        help="Reasoning effort level (low, medium, high) for gpt-5.x models.",
    ),
) -> None:
    """Test a saved system prompt by sending a user message to OpenAI.

    Loads the rendered system prompt for *identifier* and fires a two-role
    conversation (system + user) against OpenAI.  Prints the full response
    alongside token usage.  The design and prompt files are never modified.
    """
    if not message.strip():
        console.print("[yellow]Warning:[/yellow] Message is empty — nothing to send.")
        raise typer.Exit(code=1)

    config = AppConfig.from_cwd()
    storage = ProjectStorage(config)
    paths = storage.get_project_paths(identifier)
    prompt_path = paths.prompts_dir / "system.md"

    if not prompt_path.exists():
        console.print(f"[red]System prompt not found:[/red] {prompt_path}")
        console.print(
            f"[dim]Run 'promptctl design <spec>' first to generate a system prompt for '{identifier}'.[/dim]"
        )
        raise typer.Exit(code=1)

    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Parse and validate verbosity if provided
    verbosity_level: VerbosityLevel | None = None
    if verbosity:
        try:
            verbosity_level = VerbosityLevel(verbosity)
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid verbosity level '{verbosity}'. "
                f"Must be one of: low, medium, high"
            )
            raise typer.Exit(code=1)

    llm_client = _resolve_llm_client(
        use_llm=True, model=model, verbosity=verbosity_level
    )
    if llm_client is None:
        console.print(
            "[red]Error:[/red] A working LLM client is required for run. "
            "Set OPENAI_API_KEY and ensure the 'openai' package is installed."
        )
        raise typer.Exit(code=1)

    try:
        response_text, metadata = _run_test_conversation(system_prompt, message, llm_client)
    except RuntimeError as exc:
        console.print(f"[red]LLM call failed:[/red] {exc}")
        console.print("[dim]Check your OPENAI_API_KEY and network connection.[/dim]")
        raise typer.Exit(code=1) from exc

    console.rule("System Prompt")
    console.print(system_prompt)
    console.rule()
    console.print(f"\n[bold]User Message:[/bold]\n{message}\n")
    console.rule()
    console.print(f"\n[bold]Assistant Response:[/bold]\n{response_text}\n")
    console.print(
        f"[dim]Tokens: {metadata.input_tokens} input + "
        f"{metadata.output_tokens} output = "
        f"{metadata.total_tokens} total[/dim]"
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_llm_client(
    *,
    use_llm: bool,
    verbose: bool = False,
    model: str | None = None,
    verbosity: VerbosityLevel | None = None,
) -> OpenAIProvider | None:
    """Return an OpenAIProvider when possible, or None for heuristic-only mode.

    Conditions for returning None:
    - ``use_llm`` is False (caller passed ``--no-llm``).
    - OPENAI_API_KEY is not set in the environment.
    - The ``openai`` package is not installed.

    Args:
        use_llm: Whether to use the LLM client or fallback to heuristic mode.
        verbose: Print detailed config checking information.
        model: Override the default model (e.g., "gpt-5.4", "gpt-4o").
        verbosity: Override the default verbosity level (low/medium/high).

    When the key is absent a structured three-part message is printed (status,
    reason, how-to-fix) so the user knows exactly why the LLM was skipped and
    what to do about it.  Pass ``verbose=True`` to also print which config
    sources were checked.
    """
    if not use_llm:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        _print_missing_key_warning(verbose=verbose)
        return None

    try:
        from .providers import OpenAIProvider
    except ImportError:
        console.print(
            "[yellow]Warning:[/yellow] 'openai' package is not installed. "
            "Falling back to heuristic-only design. "
            "Run: pip install openai"
        )
        return None

    config = AppConfig.from_cwd()
    llm_config = config.llm if config.llm is not None else LLMConfig.from_env()
    return OpenAIProvider(
        api_key=api_key,
        model=model,
        verbosity=verbosity,
        llm_config=llm_config,
    )


def _print_missing_key_warning(*, verbose: bool = False) -> None:
    """Print a structured warning when OPENAI_API_KEY is absent.

    Emits three pieces of information separated by a visual rule:
    1. Status — what is happening right now.
    2. Why — what the consequence of missing key is.
    3. How to fix — actionable remediation steps.

    When ``verbose`` is True a fourth section lists each config source that was
    checked and whether it contained the key.
    """
    cwd = Path.cwd()
    env_file = cwd / ".env"
    env_local_file = cwd / ".env.local"

    console.rule("[yellow]OPENAI_API_KEY not found[/yellow]")
    console.print()
    console.print("[yellow]Using orthogonal framework (heuristic-only design).[/yellow]")
    console.print()
    console.print("Without an OpenAI API key, prompts are generated using your")
    console.print("framework rules only — no LLM enrichment is applied.")
    console.print()
    console.print("To enable LLM enrichment:")
    console.print(
        "  1. Copy [bold].env.example[/bold] to [bold].env[/bold] and set "
        "[bold]OPENAI_API_KEY=sk-...[/bold]"
    )
    console.print("  2. Or: [bold]export OPENAI_API_KEY=sk-...[/bold] in your shell")
    console.print("  3. Then re-run this command")

    if verbose:
        console.print()
        console.print("Checked for [bold]OPENAI_API_KEY[/bold] in:")
        console.print("  - Environment variables: [dim]not found[/dim]")
        env_status = (
            "[dim]not found[/dim]"
            if not env_file.exists()
            else "[dim]file present, key not set[/dim]"
        )
        env_label = (
            "[dim](no such file)[/dim]" if not env_file.exists() else "[dim](found)[/dim]"
        )
        console.print(f"  - .env {env_label}: {env_status}")
        env_local_status = (
            "[dim]not found[/dim]"
            if not env_local_file.exists()
            else "[dim]file present, key not set[/dim]"
        )
        env_local_label = (
            "[dim](no such file)[/dim]"
            if not env_local_file.exists()
            else "[dim](found)[/dim]"
        )
        console.print(f"  - .env.local {env_local_label}: {env_local_status}")

    console.rule()
    console.print()


def _render_prompt(design: PromptDesign) -> str:
    """Render a minimal system prompt from a PromptDesign."""
    lines = [
        f"# Task: {design.task.name}",
        "",
        design.task.goal,
    ]

    if design.task.acceptance_criteria:
        lines.append("")
        lines.append("## Acceptance Criteria")
        lines.extend(f"- {item}" for item in design.task.acceptance_criteria)

    if design.task.constraints:
        lines.append("")
        lines.append("## Constraints")
        lines.extend(f"- {item}" for item in design.task.constraints)

    if design.execution_plan is not None:
        lines.append("")
        lines.append("## Execution Plan")
        for step in sorted(design.execution_plan.steps, key=lambda s: s.order):
            lines.append(f"{step.order}. {step.description}")

    if design.rule_blocks:
        lines.append("")
        lines.append("## Rule Blocks")
        for ref in design.rule_blocks:
            lines.append(f"- {ref.name}")

    return "\n".join(lines)


def _load_scenarios(path: Path) -> Sequence[EvaluationScenario]:
    import json

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    if not isinstance(data, list):
        message = "Scenarios file must contain a JSON list."
        raise ValueError(message)

    return [EvaluationScenario.model_validate(item) for item in data]


def _print_report(report: EvaluationReport) -> None:
    console.rule(f"Evaluation Report: {report.design_identifier}")
    for result in report.results:
        console.print(f"- [bold]{result.scenario_id}[/bold]: {result.outcome}")
        if result.notes:
            console.print(f"  [dim]{result.notes}[/dim]")


def _print_audit_report(report: LinguisticAuditReport) -> None:
    console.rule(f"Linguistic Audit: {report.design_identifier}")
    console.print(f"Density Score: [bold]{report.density_score}/5[/bold]")
    console.print(f"Orthogonality Score: [bold]{report.orthogonality_score}/5[/bold]")
    console.print(f"\n[bold]Summary:[/bold] {report.summary}")

    if report.findings:
        console.print("\n[bold]Findings:[/bold]")
        for finding in report.findings:
            color = "yellow" if finding.category == "noise" else "red"
            console.print(
                f"- [[{color}]{finding.category}[/{color}]] [bold]{finding.location}[/bold]: {finding.evidence}"
            )
            console.print(f"  [green]Suggestion:[/green] {finding.suggestion}")
    else:
        console.print("\n[green]✓ No findings. This prompt is linguistically clean.[/green]")


def _run_test_conversation(
    system_prompt: str,
    user_message: str,
    llm_client: OpenAIProvider,
) -> tuple[str, UsageMetadata]:
    """Send a system + user conversation to the provider and return the result.

    This thin wrapper isolates the provider call from the command so it can be
    tested without invoking a full Typer command.  It assumes the caller has
    already validated that ``llm_client`` is an ``OpenAIProvider`` instance
    (i.e. has ``generate_with_system``).

    Args:
        system_prompt: Content for the system role.
        user_message: Content for the user role.
        llm_client: A provider instance that implements ``generate_with_system``.

    Returns:
        A tuple of (response text, UsageMetadata).

    Raises:
        RuntimeError: Propagated from the provider on API failure.
        AttributeError: If ``llm_client`` does not support ``generate_with_system``.
    """
    return llm_client.generate_with_system(system_prompt, user_message)


if __name__ == "__main__":
    app()

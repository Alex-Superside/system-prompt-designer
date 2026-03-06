from __future__ import annotations

from pathlib import Path

from .models import AgentSpec

SUMMARY_HEADING = "summary"
ROLE_HEADING = "role"
INPUTS_HEADING = "inputs"
OUTPUTS_HEADING = "outputs"
CONSTRAINTS_HEADING = "constraints"

STRUCTURED_KEYWORDS = ["json", "yaml", "xml", "html", "markdown", "table", "schema"]
DETERMINISM_KEYWORDS = ["deterministic", "same output", "stable format", "schema-compliant"]


def parse_agent_spec_from_markdown(spec_path: Path) -> AgentSpec:
    """Parse a *.agent-spec.md file into an AgentSpec model."""
    if not spec_path.exists():
        message = f"Spec file not found: {spec_path}"
        raise FileNotFoundError(message)

    lines = spec_path.read_text(encoding="utf-8").splitlines()
    sections = _split_into_sections(lines)

    identifier = spec_path.stem
    summary_text = _join_section_text(sections.get(SUMMARY_HEADING, []))
    role_text = _join_section_text(sections.get(ROLE_HEADING, []))
    inputs = _extract_bullets(sections.get(INPUTS_HEADING, []))
    outputs = _extract_bullets(sections.get(OUTPUTS_HEADING, []))
    constraints = _extract_bullets(sections.get(CONSTRAINTS_HEADING, []))

    determinism_required = _infer_determinism_required(
        outputs=outputs,
        constraints=constraints,
    )

    return AgentSpec(
        identifier=identifier,
        summary=summary_text or "TODO: Fill summary from spec.",
        role_description=role_text or "TODO: Fill role description from spec.",
        primary_inputs=inputs,
        primary_outputs=outputs,
        constraints=constraints,
        determinism_required=determinism_required,
    )


def _split_into_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("## "):
            heading_text = line[3:].strip().lower()
            current_key = heading_text
            sections.setdefault(current_key, [])
            continue

        if current_key is None:
            continue

        sections[current_key].append(raw_line)

    return sections


def _join_section_text(lines: list[str]) -> str:
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    bullet_stripped = [
        line[1:].strip() if line.lstrip().startswith("-") else line for line in cleaned_lines
    ]
    return " ".join(bullet_stripped)


def _extract_bullets(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("-"):
            bullets.append(stripped.lstrip("-").strip())
        else:
            bullets.append(stripped)
    return bullets


def _infer_determinism_required(outputs: list[str], constraints: list[str]) -> bool:
    text_blob = " ".join(outputs + constraints).lower()
    has_structured_output = any(keyword in text_blob for keyword in STRUCTURED_KEYWORDS)
    mentions_determinism = any(keyword in text_blob for keyword in DETERMINISM_KEYWORDS)
    return bool(has_structured_output or mentions_determinism)

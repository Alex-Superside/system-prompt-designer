"""Tests for prompt_design_system.spec_parser.

Covers full field extraction, graceful handling of missing sections,
determinism inference, and error conditions.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompt_design_system.models import AgentSpec
from prompt_design_system.spec_parser import (
    _extract_bullets,
    _infer_determinism_required,
    _join_section_text,
    _split_into_sections,
    parse_agent_spec_from_markdown,
)
from tests.fixtures.sample_data import (
    DETERMINISM_TRIGGER_MARKDOWN_SPEC,
    EMPTY_SECTIONS_MARKDOWN_SPEC,
    FULL_MARKDOWN_SPEC,
    MINIMAL_MARKDOWN_SPEC,
)

# ---------------------------------------------------------------------------
# _split_into_sections helper
# ---------------------------------------------------------------------------


class TestSplitIntoSections:
    def test_headings_become_keys(self):
        """## headings produce lowercased keys in the output dict."""
        lines = ["## Summary", "Some text.", "## Role", "Role text."]
        sections = _split_into_sections(lines)
        assert "summary" in sections
        assert "role" in sections

    def test_content_lines_captured(self):
        """Lines under a heading are captured in the corresponding list."""
        lines = ["## Inputs", "- item one", "- item two"]
        sections = _split_into_sections(lines)
        assert "- item one" in sections["inputs"]

    def test_content_before_any_heading_is_ignored(self):
        """Lines before the first heading are not included in any section."""
        lines = ["# Title", "Ignored line.", "## Summary", "Captured."]
        sections = _split_into_sections(lines)
        assert "Ignored line." not in str(sections)

    def test_empty_section_captured(self):
        """A heading with no following content produces an empty list."""
        lines = ["## Summary", "## Role"]
        sections = _split_into_sections(lines)
        assert sections["summary"] == []

    def test_heading_text_lowercased(self):
        """Heading text is normalised to lowercase as dictionary key."""
        lines = ["## INPUTS", "- data"]
        sections = _split_into_sections(lines)
        assert "inputs" in sections


# ---------------------------------------------------------------------------
# _join_section_text helper
# ---------------------------------------------------------------------------


class TestJoinSectionText:
    def test_joins_plain_lines(self):
        """Non-bullet lines are joined with spaces."""
        result = _join_section_text(["  First sentence.", "  Second sentence."])
        assert "First sentence." in result
        assert "Second sentence." in result

    def test_strips_leading_dash(self):
        """A single-item bullet line has its dash stripped."""
        result = _join_section_text(["- A bullet item."])
        assert result == "A bullet item."

    def test_blank_lines_are_excluded(self):
        """Blank lines do not appear in the output."""
        result = _join_section_text(["line one", "", "line two"])
        assert result == "line one line two"

    def test_empty_input_returns_empty_string(self):
        """Empty list returns an empty string."""
        assert _join_section_text([]) == ""


# ---------------------------------------------------------------------------
# _extract_bullets helper
# ---------------------------------------------------------------------------


class TestExtractBullets:
    def test_dash_prefixed_lines_extracted(self):
        """Lines starting with '-' have the dash and whitespace stripped."""
        bullets = _extract_bullets(["- item one", "- item two"])
        assert bullets == ["item one", "item two"]

    def test_non_dash_lines_included_verbatim(self):
        """Lines without a dash are included as-is (stripped of whitespace)."""
        bullets = _extract_bullets(["  plain text"])
        assert bullets == ["plain text"]

    def test_blank_lines_skipped(self):
        """Empty or whitespace-only lines are not included."""
        bullets = _extract_bullets(["- item", "", "  "])
        assert bullets == ["item"]

    def test_empty_input_returns_empty_list(self):
        """Empty input produces an empty list."""
        assert _extract_bullets([]) == []

    def test_leading_whitespace_stripped(self):
        """Leading whitespace before the dash is stripped."""
        bullets = _extract_bullets(["   - indented item"])
        assert bullets == ["indented item"]


# ---------------------------------------------------------------------------
# _infer_determinism_required helper
# ---------------------------------------------------------------------------


class TestInferDeterminismRequired:
    def test_no_keywords_returns_false(self):
        """Plain text outputs and constraints return False."""
        assert _infer_determinism_required(["plain response"], ["keep it short"]) is False

    def test_json_keyword_returns_true(self):
        """'json' in outputs triggers True."""
        assert _infer_determinism_required(["json output"], []) is True

    def test_yaml_keyword_returns_true(self):
        """'yaml' in outputs triggers True."""
        assert _infer_determinism_required(["yaml configuration"], []) is True

    def test_html_keyword_returns_true(self):
        """'html' in outputs triggers True."""
        assert _infer_determinism_required(["html page"], []) is True

    def test_markdown_keyword_returns_true(self):
        """'markdown' in outputs triggers True."""
        assert _infer_determinism_required(["markdown document"], []) is True

    def test_schema_keyword_returns_true(self):
        """'schema' in constraints triggers True."""
        assert _infer_determinism_required([], ["schema-compliant output"]) is True

    def test_deterministic_keyword_in_constraints_returns_true(self):
        """'deterministic' in constraints triggers True."""
        assert _infer_determinism_required([], ["produce deterministic results"]) is True

    def test_stable_format_keyword_returns_true(self):
        """'stable format' in constraints triggers True."""
        assert _infer_determinism_required([], ["ensure stable format across runs"]) is True

    def test_case_insensitive(self):
        """Keyword matching is case-insensitive."""
        assert _infer_determinism_required(["JSON Report"], []) is True


# ---------------------------------------------------------------------------
# parse_agent_spec_from_markdown
# ---------------------------------------------------------------------------


class TestParseAgentSpecFromMarkdown:
    def _write_spec(
        self, tmp_path: Path, content: str, filename: str = "test-agent.agent-spec.md"
    ) -> Path:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return path

    def test_missing_file_raises_file_not_found(self, tmp_path: Path):
        """Parsing a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Spec file not found"):
            parse_agent_spec_from_markdown(tmp_path / "missing.agent-spec.md")

    def test_returns_agent_spec(self, tmp_path: Path):
        """Parsing a valid spec file returns an AgentSpec."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert isinstance(result, AgentSpec)

    def test_identifier_from_file_stem(self, tmp_path: Path):
        """The identifier is derived from the filename stem."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC, "my-agent.agent-spec.md")
        result = parse_agent_spec_from_markdown(path)
        assert result.identifier == "my-agent.agent-spec"

    def test_summary_extracted(self, tmp_path: Path):
        """The Summary section is correctly extracted."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert "Test agent" in result.summary

    def test_role_extracted(self, tmp_path: Path):
        """The Role section is correctly extracted."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert "processes inputs" in result.role_description

    def test_inputs_extracted_as_list(self, tmp_path: Path):
        """The Inputs section produces a list of bullet items."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert "user message" in result.primary_inputs

    def test_outputs_extracted_as_list(self, tmp_path: Path):
        """The Outputs section produces a list of bullet items."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert "processed response" in result.primary_outputs

    def test_constraints_extracted_as_list(self, tmp_path: Path):
        """The Constraints section produces a list of bullet items."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert "Do not include personal data." in result.constraints

    def test_full_spec_all_fields_populated(self, tmp_path: Path):
        """All sections of a complete spec are parsed correctly."""
        path = self._write_spec(tmp_path, FULL_MARKDOWN_SPEC, "full-agent.agent-spec.md")
        result = parse_agent_spec_from_markdown(path)
        assert len(result.primary_inputs) == 3
        assert len(result.primary_outputs) == 2
        assert len(result.constraints) == 3

    def test_empty_sections_produce_defaults(self, tmp_path: Path):
        """An all-empty spec file falls back to TODO placeholder strings."""
        path = self._write_spec(
            tmp_path, EMPTY_SECTIONS_MARKDOWN_SPEC, "sparse-agent.agent-spec.md"
        )
        result = parse_agent_spec_from_markdown(path)
        assert "TODO" in result.summary
        assert "TODO" in result.role_description
        assert result.primary_inputs == []
        assert result.primary_outputs == []
        assert result.constraints == []

    def test_determinism_inferred_from_outputs(self, tmp_path: Path):
        """determinism_required is inferred as True when outputs contain structured keywords."""
        path = self._write_spec(
            tmp_path, DETERMINISM_TRIGGER_MARKDOWN_SPEC, "structured-agent.agent-spec.md"
        )
        result = parse_agent_spec_from_markdown(path)
        assert result.determinism_required is True

    def test_determinism_false_for_plain_spec(self, tmp_path: Path):
        """determinism_required is False for a spec with no structured output keywords."""
        path = self._write_spec(tmp_path, MINIMAL_MARKDOWN_SPEC)
        result = parse_agent_spec_from_markdown(path)
        assert result.determinism_required is False

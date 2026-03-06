"""Tests for prompt_design_system.rule_blocks.

Covers RuleBlock dataclass, RuleBlockRegistry construction, get/list/get_many
operations, filesystem loading via from_config(), and error handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompt_design_system.config import AppConfig, AppPaths
from prompt_design_system.rule_blocks import RuleBlock, RuleBlockRegistry
from tests.fixtures.sample_data import empty_registry, sample_registry

# ---------------------------------------------------------------------------
# RuleBlock dataclass
# ---------------------------------------------------------------------------


class TestRuleBlock:
    def test_fields_are_accessible(self):
        """name, path, and content are all readable after construction."""
        block = RuleBlock(
            name="test-block",
            path=Path("/some/path.md"),
            content="# Rule\n\nSome rule content.",
        )
        assert block.name == "test-block"
        assert block.path == Path("/some/path.md")
        assert "Some rule content." in block.content


# ---------------------------------------------------------------------------
# RuleBlockRegistry — construction and basic access
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryConstruction:
    def test_empty_registry_has_no_names(self):
        """An empty registry returns no names."""
        registry = empty_registry()
        assert list(registry.list_names()) == []

    def test_populated_registry_lists_names(self):
        """A pre-populated registry lists all block names."""
        registry = sample_registry()
        names = list(registry.list_names())
        assert "citations" in names
        assert "html-markup" in names
        assert "brief-json-schema" in names

    def test_direct_construction_with_dict(self):
        """RuleBlockRegistry can be constructed directly from a blocks dict."""
        blocks = {
            "my-block": RuleBlock(
                name="my-block",
                path=Path("/fake/my-block.md"),
                content="content",
            )
        }
        registry = RuleBlockRegistry(rule_blocks=blocks)
        assert "my-block" in list(registry.list_names())


# ---------------------------------------------------------------------------
# RuleBlockRegistry.get()
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryGet:
    def test_get_existing_block(self):
        """get() returns the correct RuleBlock for a known name."""
        registry = sample_registry()
        block = registry.get("citations")
        assert block.name == "citations"
        assert len(block.content) > 0

    def test_get_missing_block_raises_key_error(self):
        """get() raises KeyError for an unknown block name."""
        registry = sample_registry()
        with pytest.raises(KeyError, match="Rule block not found"):
            registry.get("nonexistent-block")

    def test_get_on_empty_registry_raises(self):
        """get() on an empty registry always raises KeyError."""
        registry = empty_registry()
        with pytest.raises(KeyError):
            registry.get("anything")

    def test_get_returns_rule_block_instance(self):
        """get() returns a RuleBlock (not just a dict or string)."""
        registry = sample_registry()
        block = registry.get("html-markup")
        assert isinstance(block, RuleBlock)


# ---------------------------------------------------------------------------
# RuleBlockRegistry.list_names()
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryListNames:
    def test_list_names_returns_all_names(self):
        """list_names() returns every name present in the registry."""
        registry = sample_registry()
        names = set(registry.list_names())
        assert names == {"citations", "html-markup", "brief-json-schema"}

    def test_list_names_empty_for_empty_registry(self):
        """list_names() on an empty registry yields nothing."""
        registry = empty_registry()
        assert list(registry.list_names()) == []


# ---------------------------------------------------------------------------
# RuleBlockRegistry.get_many()
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryGetMany:
    def test_get_many_returns_all_requested(self):
        """get_many() yields one RuleBlock per requested name."""
        registry = sample_registry()
        blocks = list(registry.get_many(["citations", "html-markup"]))
        assert len(blocks) == 2
        names = {b.name for b in blocks}
        assert names == {"citations", "html-markup"}

    def test_get_many_empty_list(self):
        """get_many([]) yields nothing."""
        registry = sample_registry()
        blocks = list(registry.get_many([]))
        assert blocks == []

    def test_get_many_raises_on_missing_name(self):
        """get_many() raises KeyError when any requested name is absent."""
        registry = sample_registry()
        with pytest.raises(KeyError):
            list(registry.get_many(["citations", "no-such-block"]))

    def test_get_many_preserves_order(self):
        """get_many() yields blocks in the same order as requested."""
        registry = sample_registry()
        blocks = list(registry.get_many(["html-markup", "citations"]))
        assert blocks[0].name == "html-markup"
        assert blocks[1].name == "citations"


# ---------------------------------------------------------------------------
# RuleBlockRegistry.from_config() — filesystem loading
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryFromConfig:
    """Tests for the user-directory (ai_components/rule_blocks/) loading path.

    These tests suppress the package-directory contribution via monkeypatch so
    that each assertion is scoped to user-directory behaviour only.  The
    interaction between both directories is covered by
    TestRuleBlockRegistryDualDirectoryLoading below.
    """

    def test_loads_markdown_files_from_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """from_config() loads all .md files from the user rule_blocks directory."""
        monkeypatch.setattr(
            RuleBlockRegistry, "_load_from_package_directory", staticmethod(lambda: {})
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "block-a.md").write_text("# Block A\n\nContent A.", encoding="utf-8")
        (rb_dir / "block-b.md").write_text("# Block B\n\nContent B.", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        names = set(registry.list_names())
        assert names == {"block-a", "block-b"}

    def test_name_is_file_stem(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """The block name equals the filename without extension."""
        monkeypatch.setattr(
            RuleBlockRegistry, "_load_from_package_directory", staticmethod(lambda: {})
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "citation_formatting_rules.md").write_text("# Rules", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        block = registry.get("citation_formatting_rules")
        assert block.name == "citation_formatting_rules"

    def test_content_matches_file_content(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """The loaded block content exactly matches the file text."""
        monkeypatch.setattr(
            RuleBlockRegistry, "_load_from_package_directory", staticmethod(lambda: {})
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        expected_content = "# My Rule\n\nDo this and not that.\n"
        (rb_dir / "my-rule.md").write_text(expected_content, encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        block = registry.get("my-rule")
        assert block.content == expected_content

    def test_nonexistent_directory_returns_empty_registry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When neither directory exists an empty registry is returned."""
        monkeypatch.setattr(
            RuleBlockRegistry, "_load_from_package_directory", staticmethod(lambda: {})
        )

        # Do not create ai_components/rule_blocks.
        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)
        assert list(registry.list_names()) == []

    def test_non_md_files_are_ignored(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Files with extensions other than .md are not loaded from the user directory."""
        monkeypatch.setattr(
            RuleBlockRegistry, "_load_from_package_directory", staticmethod(lambda: {})
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "valid.md").write_text("# Valid", encoding="utf-8")
        (rb_dir / "ignored.json").write_text("{}", encoding="utf-8")
        (rb_dir / "also-ignored.txt").write_text("text", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        names = list(registry.list_names())
        assert names == ["valid"]

    def test_path_stored_on_block(self, tmp_path: Path):
        """The RuleBlock's path attribute points to the actual file."""
        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        md_file = rb_dir / "myblock.md"
        md_file.write_text("# Block", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        block = registry.get("myblock")
        assert block.path == md_file


# ---------------------------------------------------------------------------
# RuleBlockRegistry._load_rule_blocks_from_directory() helper
# ---------------------------------------------------------------------------


class TestLoadRuleBlocksFromDirectory:
    def test_loads_all_md_files(self, tmp_path: Path):
        """All .md files in a directory are returned as RuleBlock objects."""
        (tmp_path / "alpha.md").write_text("Alpha content.", encoding="utf-8")
        (tmp_path / "beta.md").write_text("Beta content.", encoding="utf-8")

        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert set(result.keys()) == {"alpha", "beta"}

    def test_non_md_files_are_excluded(self, tmp_path: Path):
        """Files that are not .md are silently skipped."""
        (tmp_path / "valid.md").write_text("Valid.", encoding="utf-8")
        (tmp_path / "noise.txt").write_text("Ignored.", encoding="utf-8")
        (tmp_path / "data.json").write_text("{}", encoding="utf-8")

        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert list(result.keys()) == ["valid"]

    def test_block_name_equals_file_stem(self, tmp_path: Path):
        """Each block name is derived from the filename without the .md extension."""
        (tmp_path / "citation_formatting_rules.md").write_text("# Rules", encoding="utf-8")

        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert "citation_formatting_rules" in result
        assert result["citation_formatting_rules"].name == "citation_formatting_rules"

    def test_block_content_matches_file(self, tmp_path: Path):
        """The content field of each block equals the raw file text."""
        expected = "# My Rule\n\nDo this.\n"
        (tmp_path / "my-rule.md").write_text(expected, encoding="utf-8")

        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert result["my-rule"].content == expected

    def test_block_path_points_to_file(self, tmp_path: Path):
        """The path attribute resolves to the source file on disk."""
        md_file = tmp_path / "my-block.md"
        md_file.write_text("content", encoding="utf-8")

        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert result["my-block"].path == md_file

    def test_empty_directory_returns_empty_dict(self, tmp_path: Path):
        """A directory with no .md files yields an empty mapping."""
        result = RuleBlockRegistry._load_rule_blocks_from_directory(tmp_path)

        assert result == {}


# ---------------------------------------------------------------------------
# RuleBlockRegistry.from_config() — dual-directory loading
# ---------------------------------------------------------------------------


class TestRuleBlockRegistryDualDirectoryLoading:
    """Verify that from_config() merges package and user rule blocks correctly."""

    def _make_package_dir(self, tmp_path: Path) -> Path:
        """Return the path that _load_from_package_directory() resolves to."""
        import prompt_design_system.rule_blocks as rb_module

        return Path(rb_module.__file__).parent / "rule_blocks"

    def test_user_blocks_are_loaded(self, tmp_path: Path):
        """Blocks placed in ai_components/rule_blocks/ appear in the registry."""
        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "user-rule.md").write_text("User rule content.", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        assert "user-rule" in list(registry.list_names())

    def test_package_blocks_are_loaded(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Blocks in prompt_design_system/rule_blocks/ are loaded as secondary sources."""
        # Redirect _load_from_package_directory to a controlled temp location.
        pkg_dir = tmp_path / "pkg_rule_blocks"
        pkg_dir.mkdir()
        (pkg_dir / "pkg-rule.md").write_text("Package rule content.", encoding="utf-8")

        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: RuleBlockRegistry._load_rule_blocks_from_directory(pkg_dir)),
        )

        # No user directory — only the (mocked) package directory.
        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        assert "pkg-rule" in list(registry.list_names())
        assert registry.get("pkg-rule").content == "Package rule content."

    def test_user_block_overrides_package_block_with_same_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When the same stem exists in both directories the user copy wins."""
        pkg_dir = tmp_path / "pkg_rule_blocks"
        pkg_dir.mkdir()
        (pkg_dir / "shared-rule.md").write_text("Package version.", encoding="utf-8")

        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: RuleBlockRegistry._load_rule_blocks_from_directory(pkg_dir)),
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "shared-rule.md").write_text("User version.", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        block = registry.get("shared-rule")
        assert block.content == "User version."
        assert block.path == rb_dir / "shared-rule.md"

    def test_unique_blocks_from_both_directories_are_merged(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Blocks unique to each directory are all reachable after loading."""
        pkg_dir = tmp_path / "pkg_rule_blocks"
        pkg_dir.mkdir()
        (pkg_dir / "pkg-only.md").write_text("Package-only.", encoding="utf-8")

        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: RuleBlockRegistry._load_rule_blocks_from_directory(pkg_dir)),
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "user-only.md").write_text("User-only.", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        names = set(registry.list_names())
        assert "pkg-only" in names
        assert "user-only" in names

    def test_missing_user_directory_still_loads_package_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Absence of ai_components/rule_blocks/ does not prevent package blocks from loading."""
        pkg_dir = tmp_path / "pkg_rule_blocks"
        pkg_dir.mkdir()
        (pkg_dir / "fallback-rule.md").write_text("Fallback content.", encoding="utf-8")

        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: RuleBlockRegistry._load_rule_blocks_from_directory(pkg_dir)),
        )

        # Deliberately do NOT create the ai_components/rule_blocks/ directory.
        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        assert "fallback-rule" in list(registry.list_names())

    def test_missing_package_directory_still_loads_user_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Absence of prompt_design_system/rule_blocks/ does not prevent user blocks from loading."""
        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: {}),
        )

        rb_dir = tmp_path / "ai_components" / "rule_blocks"
        rb_dir.mkdir(parents=True)
        (rb_dir / "user-rule.md").write_text("User content.", encoding="utf-8")

        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        assert "user-rule" in list(registry.list_names())

    def test_both_directories_missing_returns_empty_registry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When neither directory exists the registry is empty rather than erroring."""
        monkeypatch.setattr(
            RuleBlockRegistry,
            "_load_from_package_directory",
            staticmethod(lambda: {}),
        )

        # Deliberately do NOT create the ai_components/rule_blocks/ directory.
        config = AppConfig(paths=AppPaths(root_dir=tmp_path))
        registry = RuleBlockRegistry.from_config(config)

        assert list(registry.list_names()) == []

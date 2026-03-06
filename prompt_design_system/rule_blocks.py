from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig


@dataclass
class RuleBlock:
    """In-memory representation of a rule block file."""

    name: str
    path: Path
    content: str


class RuleBlockRegistry:
    """Loads and serves rule blocks from two directories.

    Loading order (lowest to highest priority):
    1. ``prompt_design_system/rule_blocks/`` — package reference implementations
       shipped alongside the library code.
    2. ``ai_components/rule_blocks/`` — user-editable overrides.

    When the same stem name appears in both directories the user copy wins.
    All existing callers that only touch ``from_config()``, ``get()``,
    ``list_names()``, and ``get_many()`` continue to work unchanged.
    """

    def __init__(self, rule_blocks: dict[str, RuleBlock]) -> None:
        self._rule_blocks = rule_blocks

    # ------------------------------------------------------------------
    # Public factory
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config: AppConfig) -> RuleBlockRegistry:
        """Build a registry from both the package and user directories.

        Package blocks (``prompt_design_system/rule_blocks/``) are loaded
        first.  User blocks (``ai_components/rule_blocks/``) are layered on
        top, so any name collision is resolved in the user's favour.
        """
        package_blocks = cls._load_from_package_directory()
        user_blocks = cls._load_from_config_directory(config)

        # Merge: user entries overwrite package entries with the same name.
        merged: dict[str, RuleBlock] = {**package_blocks, **user_blocks}
        return cls(rule_blocks=merged)

    # ------------------------------------------------------------------
    # Private loaders
    # ------------------------------------------------------------------

    @staticmethod
    def _load_from_package_directory() -> dict[str, RuleBlock]:
        """Load reference rule blocks shipped inside the package.

        Resolves to ``prompt_design_system/rule_blocks/`` relative to this
        file.  Returns an empty dict when the directory does not exist so
        that an editable install without the bundled blocks degrades
        gracefully.
        """
        package_dir = Path(__file__).parent / "rule_blocks"
        if not package_dir.exists():
            return {}
        return RuleBlockRegistry._load_rule_blocks_from_directory(package_dir)

    @staticmethod
    def _load_from_config_directory(config: AppConfig) -> dict[str, RuleBlock]:
        """Load user-editable rule blocks from ``ai_components/rule_blocks/``.

        The directory is resolved through ``config.paths.rule_blocks_dir``.
        Returns an empty dict when the directory does not exist.
        """
        user_dir = config.paths.rule_blocks_dir
        if not user_dir.exists():
            return {}
        return RuleBlockRegistry._load_rule_blocks_from_directory(user_dir)

    @staticmethod
    def _load_rule_blocks_from_directory(path: Path) -> dict[str, RuleBlock]:
        """Read every ``*.md`` file in *path* and return a name → RuleBlock map.

        The block name is the file stem (filename without the ``.md``
        extension).  Non-Markdown files are silently skipped.
        """
        blocks: dict[str, RuleBlock] = {}
        for md_file in sorted(path.glob("*.md")):
            if md_file.is_file():
                name = md_file.stem
                content = md_file.read_text(encoding="utf-8")
                blocks[name] = RuleBlock(name=name, path=md_file, content=content)
        return blocks

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def list_names(self) -> Iterable[str]:
        return self._rule_blocks.keys()

    def get(self, name: str) -> RuleBlock:
        if name not in self._rule_blocks:
            message = f"Rule block not found: {name}"
            raise KeyError(message)
        return self._rule_blocks[name]

    def get_many(self, names: list[str]) -> Iterable[RuleBlock]:
        for name in names:
            yield self.get(name)

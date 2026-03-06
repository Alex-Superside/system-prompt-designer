# ARCHITECTURE.md: Prompt Design Framework Library

## Executive Summary

This project encodes the orthogonal prompt design methodology (from the Graph documentation) into a production-grade Python library, CLI tool, and autonomous agent system. The architecture enforces separation of concerns at the code level: models define data structures, patterns encode design rules, renderers mechanically serialize, and agents orchestrate workflows outside the library boundary. Success depends on strict enforcement of layering contracts and prevention of scope creep in critical seams (renderers, tier logic, rule block resolution). This document specifies the architecture, design contracts, phased implementation, and enforcement mechanisms.

---

## Project Goals & Non-Goals

### Goals
- Automate the design of agent system prompts using the orthogonal Task/Plan/RuleBlock framework
- Provide a composable library that ingests Markdown specs and outputs system prompts across multiple LLM providers
- Support autonomous design, refinement, and evaluation workflows via dedicated agents
- Enable deterministic, testable prompt generation with clear audit trails
- Prepare for Phase 5 extensibility (Notion sync, FastAPI service, custom backends)

### Non-Goals
- Replace human judgment in prompt design (agents assist, humans decide)
- Support arbitrary Markdown parsing (only structured formats following our spec)
- Implement UI/frontend (CLI and optional HTTP API only)
- Provide cloud infrastructure or managed service
- Handle agent execution/deployment (library + CLI tools only; orchestration is user's responsibility)

---

## Architecture Overview

### Layering Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ CLI Layer (promptctl)                                       │
│ - init-spec, design, evaluate commands                      │
│ - User-facing entry point                                   │
└───────────────────┬─────────────────────────────────────────┘
                    │ (owns, imports agents)
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ Agent Orchestration Layer (application/)                    │
│ - DesignAgent: AgentSpec → FullPromptDesign               │
│ - RefinementAgent: feedback → diffs                        │
│ - EvaluatorAgent: test conversations → metrics             │
└───────────────────┬─────────────────────────────────────────┘
                    │ (imports library, no reverse dependency)
                    ↓
┌──────────────────────────────────────────────────────────────────┐
│ Library Layer: prompt_framework/                                 │
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐    ┌────────────┐  │
│  │ providers/   │────────→│ models/      │←───│ patterns/  │  │
│  │              │         │              │    │            │  │
│  │ • OpenAI     │         │ • AgentSpec  │    │ • Tier 1/2/3  │
│  │ • Anthropic  │         │ • TaskBlock  │    │ • Selector    │
│  │ • Gemini     │         │ • ExecPlan   │    │ • Registry    │
│  │              │         │ • RuleBlockRef│   │            │  │
│  │ unified API  │         │ • PromptDesign│  │            │  │
│  └──────────────┘         │ • PromptTier │   └────────────┘  │
│         ↑                 │ • EvalSchema │         ↑           │
│         │                 └──────────────┘         │           │
│         └─────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ parsers/     │  │ renderers/   │  │ storage/     │        │
│  │              │  │              │  │              │        │
│  │ • Markdown   │  │ • ToSystemPrompt    │ • FileBackend  │        │
│  │   parser     │  │ • (mechanical only) │ • Interface    │        │
│  │ • Validators │  │ • Zero logic  │  │ • Abstraction  │        │
│  │              │  │              │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────────┘
         ↓ (import only, one-way)        ↓ (backendable)
     ┌────────────────────────────────────────┐
     │ External Storage & Services             │
     │ - Filesystem (default)                  │
     │ - Notion (Phase 5)                      │
     │ - Database (future)                     │
     └────────────────────────────────────────┘
```

### Dependency Contract (Strictly Enforced)

```
providers/          [no dependencies within library]
     ↑
   models/          [depends on: nothing]
     ↑
parsers/, patterns/, renderers/ [depend on: models only]
     ↑
   storage/         [depends on: models, parsers, renderers]
     ↑
[agents/ - EXTERNAL] [depends on: library only, no reverse dependency]
     ↑
[CLI - EXTERNAL]    [depends on: library, agents only]
```

**Critical Rule:** No upward dependency arrows. Any violation is a layering breach.

---

## Layering Contract & Module Responsibilities

### `providers/` — Model API Abstraction Layer

**Responsibility:** Abstract away differences between LLM providers (OpenAI, Anthropic, Gemini).

**Key Exports:**
```python
class ProviderCapabilities:
    supports_function_calling: bool
    supports_structured_output: bool
    supports_streaming: bool
    max_context_tokens: int
    [additional capability flags]

class ProviderInterface(ABC):
    """Unified interface all providers must implement."""
    async def send_message(
        self,
        messages: List[Message],
        system: str,
        model: str
    ) -> Response

    def capabilities(self) -> ProviderCapabilities
    def supports(self, capability: str) -> bool

class OpenAIProvider(ProviderInterface): ...
class AnthropicProvider(ProviderInterface): ...
class GeminiProvider(ProviderInterface): ...

def get_provider(name: str) -> ProviderInterface
```

**Strict Constraints:**
- No provider-specific parameters leak into the interface (e.g., no `function_tools=` kwarg)
- Agents declare capability requirements; providers report what they support
- If a capability is required but not available, raise `CapabilityNotSupportedError`, don't emulate

**What Imports From Here:**
- library: agents/ (not part of library, but agents orchestration)
- agents/ only (no library module depends on providers)

**What This Module Imports:**
- External: `openai`, `anthropic`, `google.generativeai` SDK packages
- Nothing from prompt_framework

---

### `models/` — Domain Data Structures

**Responsibility:** Define all core data types using Pydantic. These are POD (Plain Old Data) objects with validation, no business logic.

**Key Exports:**

```python
class PromptTier(Enum):
    TIER_1 = "tier_1"  # Task only
    TIER_2 = "tier_2"  # Task + minimal Execution Plan
    TIER_3 = "tier_3"  # Full Task + Plan + Rule Blocks

class RuleBlockRef(BaseModel):
    """Symbolic reference to a Rule Block (resolved at render time, not construction)."""
    name: str  # e.g., "citation_rules", "html_formatting"
    version: str = "latest"
    metadata: Dict[str, Any] = {}

class TaskBlock(BaseModel):
    """WHAT: outcomes, constraints, acceptance criteria. No execution logic."""
    description: str
    outcomes: List[str]
    constraints: List[str]
    acceptance_criteria: List[str]
    rule_block_refs: List[RuleBlockRef] = []  # References only, not content

class ExecutionPlanBlock(BaseModel):
    """HOW: ordered steps, validation, branching. No formatting/schema rules."""
    steps: List[str]  # Atomic, ordered steps
    validation_rules: List[str]  # Logic for checking step outputs
    branching: Dict[str, List[str]] = {}  # Conditional paths
    rule_block_refs: List[RuleBlockRef] = []  # References only

class RuleBlock(BaseModel):
    """DETAILS: schema, formatting, citation rules. Single source of truth."""
    name: str  # Stable identifier (renaming is breaking change)
    version: str
    content: str  # Markdown content from Graph/05-Rule-Blocks-Component.md
    schema_definition: Dict[str, Any] = {}  # If applicable (JSON schema, regex, etc.)
    examples: List[Dict[str, Any]] = []

class FullPromptDesign(BaseModel):
    """Complete, resolved prompt design (all references resolved at this level)."""
    tier: PromptTier
    task_block: TaskBlock
    execution_plan_block: Optional[ExecutionPlanBlock]  # None if tier == TIER_1
    resolved_rule_blocks: Dict[str, RuleBlock]  # name → RuleBlock (resolved at render time)
    metadata: Dict[str, Any] = {}

class AgentSpec(BaseModel):
    """Input specification in code form (parsed from Markdown)."""
    name: str
    role: str
    context: str
    inputs: List[str]
    outputs: List[str]
    constraints: List[str]
    examples: List[Dict[str, Any]] = []
    tier_hint: Optional[PromptTier] = None  # User can override

class EvaluationMetrics(BaseModel):
    """Output from EvaluatorAgent: scored results."""
    provider: str
    model: str
    test_scenario: str
    accuracy_score: float  # 0.0 to 1.0
    schema_compliance_score: float
    guardrail_violations: List[str] = []
    latency_ms: float
    test_transcript: List[Message] = []

class EvaluationResult(BaseModel):
    """Aggregated evaluation across scenarios and providers."""
    design_id: str
    overall_score: float
    per_provider_metrics: Dict[str, EvaluationMetrics]
    recommendations: List[str]
```

**Design Principle:** Objects are validation-strict (Pydantic `validate_assignment=True`), no methods except `model_validate()`, `model_dump()`, `model_dump_json()`.

**What Imports From Here:**
- parsers/, patterns/, renderers/, storage/, agents/ (everyone except providers/)

**What This Module Imports:**
- External: `pydantic`
- Nothing from prompt_framework

---

### `patterns/` — Design Pattern Encoding

**Responsibility:** Implement tier selection logic and Tier 1/2/3 design patterns that generate `FullPromptDesign` from `AgentSpec`.

**Key Exports:**

```python
class SelectionCriterion(ABC):
    """Declarative rule for tier selection. Evaluated by PatternSelector."""
    def evaluate(self, spec: AgentSpec) -> Tuple[Optional[PromptTier], float, str]:
        """
        Returns: (recommended_tier, confidence_0_to_1, rationale_text)
        If no recommendation, return (None, 0.0, reason).
        """
        pass

class ComplexityScoreCriterion(SelectionCriterion):
    """Recommends tier based on spec complexity (constraints, outputs)."""
    pass

class DeterminismCriterion(SelectionCriterion):
    """Recommends TIER_3 if spec requires structured output or strict schema."""
    pass

class SchemaRequirementCriterion(SelectionCriterion):
    """Recommends TIER_3 if spec mentions JSON, HTML, or schema compliance."""
    pass

class PatternSelector:
    """Selects tier and design pattern for an AgentSpec."""

    def __init__(self, criteria: List[SelectionCriterion] = None):
        self.criteria = criteria or self._default_criteria()

    def select(
        self,
        spec: AgentSpec,
        override_tier: Optional[PromptTier] = None
    ) -> Tuple[PromptTier, str]:
        """
        Select tier for spec. Returns (tier, rationale_string).
        If override_tier provided, use it but include rationale explaining the override.
        """
        if override_tier:
            return override_tier, f"User override: {override_tier}"

        evaluations = [c.evaluate(spec) for c in self.criteria]
        # Aggregate evaluations, return majority recommendation
        # ...

    @staticmethod
    def _default_criteria() -> List[SelectionCriterion]:
        return [
            ComplexityScoreCriterion(),
            DeterminismCriterion(),
            SchemaRequirementCriterion(),
        ]

class Tier1Pattern:
    """Task-only design."""

    @staticmethod
    def build(spec: AgentSpec) -> FullPromptDesign:
        """Generate TIER_1 FullPromptDesign from AgentSpec."""
        task_block = TaskBlock(
            description=spec.role,
            outcomes=spec.outputs,
            constraints=spec.constraints,
            acceptance_criteria=[...],  # Derived from spec
            rule_block_refs=[]  # TIER_1 may have no rule blocks
        )
        return FullPromptDesign(
            tier=PromptTier.TIER_1,
            task_block=task_block,
            execution_plan_block=None,
            resolved_rule_blocks={}
        )

class Tier2Pattern:
    """Task + minimal Execution Plan."""

    @staticmethod
    def build(spec: AgentSpec) -> FullPromptDesign:
        """Generate TIER_2 FullPromptDesign."""
        task_block = TaskBlock(...)
        exec_plan = ExecutionPlanBlock(
            steps=[...],  # Light procedural steps
            validation_rules=[...],
            rule_block_refs=[...]  # May reference some rule blocks
        )
        return FullPromptDesign(
            tier=PromptTier.TIER_2,
            task_block=task_block,
            execution_plan_block=exec_plan,
            resolved_rule_blocks={...}
        )

class Tier3Pattern:
    """Full Task + Execution Plan + Rule Blocks."""

    @staticmethod
    def build(
        spec: AgentSpec,
        rule_registry: 'RuleBlockRegistry'
    ) -> FullPromptDesign:
        """
        Generate TIER_3 FullPromptDesign with full structure.
        Must resolve rule block references from registry.
        """
        task_block = TaskBlock(...)
        exec_plan = ExecutionPlanBlock(...)

        # Select which rule blocks apply based on spec
        selected_rule_names = [...]
        resolved_blocks = rule_registry.resolve_batch(selected_rule_names)

        return FullPromptDesign(
            tier=PromptTier.TIER_3,
            task_block=task_block,
            execution_plan_block=exec_plan,
            resolved_rule_blocks=resolved_blocks
        )
```

**Critical Constraints:**
- Never check for the existence of rule blocks before rendering (that's renderer's job at render time)
- Tier selection must be deterministic and auditable
- Never generate raw text; always produce `FullPromptDesign` objects
- No rendering or formatting logic here

**What Imports From Here:**
- renderers/, agents/, storage/

**What This Module Imports:**
- models/, rule_registry from patterns/registry

---

### `models.rule_registry` — Rule Block Catalog

**Responsibility:** Central registry for all Rule Blocks with entry-points extensibility.

**Key Exports:**

```python
class RuleBlockRegistry:
    """Single source of truth for all Rule Blocks."""

    def register(self, block: RuleBlock) -> None:
        """Register a block. Raises ValueError if name already exists."""
        if self._catalog.get(block.name):
            raise ValueError(f"RuleBlock '{block.name}' already registered")
        self._catalog[block.name] = block

    def get(self, name: str, version: str = "latest") -> RuleBlock:
        """Retrieve block by name. Raises KeyError if not found."""
        pass

    def resolve_batch(self, names: List[RuleBlockRef]) -> Dict[str, RuleBlock]:
        """
        Resolve multiple references at once.
        Must be called exactly once at FullPromptDesign construction time
        (i.e., when rendering, not earlier).
        """
        return {ref.name: self.get(ref.name, ref.version) for ref in names}

    def list_blocks(self) -> List[str]:
        """Return all registered block names."""
        pass

    @classmethod
    def load_from_entry_points(cls) -> 'RuleBlockRegistry':
        """
        Load all Rule Blocks registered via Python entry points.
        Format: group='prompt_framework.rule_blocks'
        Entry point should return a function() -> List[RuleBlock].
        This is the primary extensibility hook for Phase 5.
        """
        pass

    @classmethod
    def load_from_markdown_directory(cls, path: str) -> 'RuleBlockRegistry':
        """
        Load Rule Blocks from Markdown files in a directory.
        Filename: {name}_{version}.md, content parsed into RuleBlock.
        Used for built-in blocks in prompt_framework/rule_blocks/.
        """
        pass

# Built-in Rule Blocks (loaded via markdown files)
BUILTIN_BLOCKS = [
    "citation_rules",
    "html_formatting",
    "json_schema_example",
    "guardrail_compliance",
]
```

**Extensibility (Phase 5 Hook):**

Projects can register custom rule blocks via `pyproject.toml`:

```toml
[project.entry-points."prompt_framework.rule_blocks"]
my_domain_rules = "my_package.rules:load_rule_blocks"
```

The function `load_rule_blocks()` returns `List[RuleBlock]`.

---

### `parsers/` — Markdown Input Parsing

**Responsibility:** Convert Markdown-formatted agent specs into `AgentSpec` objects.

**Key Exports:**

```python
class MarkdownSpecParser:
    """Parse Markdown specs into AgentSpec objects."""

    @staticmethod
    def parse(markdown_text: str) -> AgentSpec:
        """
        Parse Markdown with expected structure:

        # Agent Name

        ## Role
        [role description]

        ## Context
        [context information]

        ## Inputs
        - [input 1]
        - [input 2]

        ## Outputs
        - [output 1]

        ## Constraints
        - [constraint 1]

        ## Tier (optional)
        [TIER_1 | TIER_2 | TIER_3]

        Returns: AgentSpec
        """
        pass

class SpecValidator:
    """Validate AgentSpec completeness and consistency."""

    @staticmethod
    def validate(spec: AgentSpec) -> List[ValidationError]:
        """Return list of validation errors (empty if valid)."""
        errors = []
        if not spec.role:
            errors.append(ValidationError("role", "required"))
        if not spec.outputs:
            errors.append(ValidationError("outputs", "required and non-empty"))
        # ... other checks
        return errors
```

**Constraints:**
- Parsing is separate from validation (parse to intermediate form, then validate)
- No tier selection logic here (that's `PatternSelector`'s job)

---

### `renderers/` — Prompt Serialization (Mechanical Only)

**Responsibility:** Convert `FullPromptDesign` to concrete system prompt strings. Zero business logic.

**Key Exports:**

```python
class PromptRenderer(ABC):
    """Abstract base for prompt renderers."""

    @staticmethod
    def render(design: FullPromptDesign) -> str:
        """
        Convert FullPromptDesign to a system prompt string.

        CONTRACT (strictly enforced):
        1. Input is a fully resolved FullPromptDesign
        2. No conditional logic (e.g., no "if tier == TIER_3 then...")
        3. No rule block lookups or existence checks
        4. Output is deterministic: same input → same output
        5. No modifications, corrections, or restructuring of the design

        Violation of contract = bug in renderer, refactor to patterns/
        """
        pass

class StandardPromptRenderer(PromptRenderer):
    """
    Standard rendering format (used by most agents).

    Output structure:

    # ROLE & CONTEXT
    [task_block.description]

    # OBJECTIVES
    [task_block.outcomes, formatted as list]

    # CONSTRAINTS
    [task_block.constraints, formatted as list]

    # ACCEPTANCE CRITERIA
    [task_block.acceptance_criteria, formatted as list]

    [If ExecutionPlanBlock exists:]
    # EXECUTION PLAN
    [steps, formatted as ordered list]

    [For each resolved rule block:]
    # RULE BLOCK: {name}
    [content, as-is from rule_block.content]
    """

    @staticmethod
    def render(design: FullPromptDesign) -> str:
        # Mechanical assembly of parts
        pass

def render_prompt(design: FullPromptDesign, renderer: PromptRenderer = None) -> str:
    """Convenience function using StandardPromptRenderer by default."""
    if renderer is None:
        renderer = StandardPromptRenderer()
    return renderer.render(design)
```

**Contract Test (Example):**

```python
def test_renderer_is_purely_mechanical():
    """Renderer must output exactly what it receives, no logic."""
    design = FullPromptDesign(
        tier=PromptTier.TIER_2,
        task_block=TaskBlock(...),
        execution_plan_block=ExecutionPlanBlock(...),
        resolved_rule_blocks={"broken_rule": RuleBlock(name="broken_rule", content="INVALID")}
    )
    output = StandardPromptRenderer.render(design)
    # Renderer outputs the broken content as-is; it does NOT fix or skip it
    assert "INVALID" in output
```

**Violations That Must Not Occur:**
- Checking if a rule block exists before including it
- Skipping an execution plan if it's "too simple"
- Reformatting constraint text based on tier
- Any conditional logic based on design content

---

### `storage/` — Persistence Abstraction

**Responsibility:** Abstract file/database persistence, enabling multiple backends (filesystem, Notion, DB).

**Key Exports:**

```python
class StorageBackend(ABC):
    """Abstract backend for reading/writing specs and designs."""

    async def write_spec(self, spec_id: str, spec: AgentSpec, owner: str) -> None:
        """Persist AgentSpec. owner context for multi-tenant support."""
        pass

    async def read_spec(self, spec_id: str, owner: str) -> AgentSpec:
        """Retrieve AgentSpec. Raises KeyError if not found."""
        pass

    async def list_specs(self, owner: str) -> List[Tuple[str, AgentSpec]]:
        """List all specs for owner. Returns (id, spec) tuples."""
        pass

    async def write_design(self, design_id: str, design: FullPromptDesign, owner: str) -> None:
        """Persist FullPromptDesign."""
        pass

    async def read_design(self, design_id: str, owner: str) -> FullPromptDesign:
        """Retrieve FullPromptDesign."""
        pass

    async def write_evaluation(self, eval_id: str, result: EvaluationResult, owner: str) -> None:
        """Persist evaluation results."""
        pass

    async def read_evaluation(self, eval_id: str, owner: str) -> EvaluationResult:
        """Retrieve evaluation results."""
        pass

class FileStorageBackend(StorageBackend):
    """Default: store specs, designs, evaluations as files (JSON/Markdown)."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir  # e.g., ~/.prompt_framework/

    # Implements all abstract methods, using JSON/Markdown serialization
    pass

class NotionStorageBackend(StorageBackend):
    """Phase 5: store designs in Notion pages. Inherits from StorageBackend."""
    pass

class DatabaseStorageBackend(StorageBackend):
    """Phase 5: store in PostgreSQL/SQLite. Inherits from StorageBackend."""
    pass

# Factory for selecting backend
def get_storage_backend(config: Dict[str, Any]) -> StorageBackend:
    """
    Create backend based on config.

    config = {
        "backend": "filesystem",  # or "notion", "database"
        "base_dir": "~/.prompt_framework/",  # for filesystem
        ...
    }
    """
    pass
```

**Design Note:** Storage backends are intentionally async-ready (use `async def`) to support network-based backends (Notion, databases) in Phase 5 without API changes.

---

## Critical Design Contracts

### Contract 1: Renderer Purity

**What It Means:** Renderers are purely mechanical serializers. They take a `FullPromptDesign` and output a string. They never make decisions about what to include, skip, or reformat based on the content they receive.

**How to Enforce:**
1. Code review checklist: "Does this renderer contain any `if`, `else`, or conditional logic?"
2. Automated test: Provide a structurally valid but semantically nonsensical design and verify output includes all parts as-is.
3. Linter: Add a custom rule that flags conditional statements in `renderers/*.py`.

**Example Violation:**
```python
# BAD: Renderer making decisions
def render(design):
    output = render_task(design.task_block)
    if design.execution_plan_block:  # ← VIOLATION: logic in renderer
        output += render_plan(design.execution_plan_block)
    return output
```

**Correct Pattern:**
```python
# GOOD: Always render all parts; if plan should be skipped, don't include it in FullPromptDesign
def render(design):
    output = render_task(design.task_block)
    if design.execution_plan_block is not None:  # Is there a plan in the design?
        output += render_plan(design.execution_plan_block)  # Render it as-is
    return output
```

### Contract 2: Rule Block Reference Symbolism

**What It Means:** `RuleBlockRef` remains symbolic (just a name/version identifier) until render time. No early resolution during `FullPromptDesign` construction.

**Why:** Decouples design construction from registry availability and allows safe, lazy resolution.

**How to Enforce:**
1. `RuleBlockRef` is a simple dataclass with only `name`, `version`, `metadata` fields.
2. `FullPromptDesign` keeps `resolved_rule_blocks: Dict[str, RuleBlock]` but this is populated only at render time.
3. Code review: Check that `RuleBlockRegistry` is never called in `patterns/*.py` (only in `renderers/*`).
4. Type system: `TaskBlock.rule_block_refs` is `List[RuleBlockRef]`, not `List[RuleBlock]`.

**Example Violation:**
```python
# BAD: Resolving at construction time
def build_tier_3(spec, registry):
    block_refs = [RuleBlockRef(name="citation"), RuleBlockRef(name="guardrails")]
    resolved_blocks = {ref.name: registry.get(ref.name) for ref in block_refs}  # ← Early resolution
    return FullPromptDesign(..., resolved_rule_blocks=resolved_blocks)
```

**Correct Pattern:**
```python
# GOOD: Keep references symbolic; resolve at render time
def build_tier_3(spec, registry):
    block_refs = [RuleBlockRef(name="citation"), RuleBlockRef(name="guardrails")]
    return FullPromptDesign(..., rule_block_refs_in_task=block_refs)  # Don't resolve yet

# Resolution happens here, at render time
def render(design: FullPromptDesign, registry: RuleBlockRegistry):
    resolved = registry.resolve_batch(design.task_block.rule_block_refs)
    # ... render with resolved blocks
```

### Contract 3: One-Way Dependency Arrows

**What It Means:** Only downward imports allowed. `patterns/` imports `models/`, but `models/` never imports `patterns/`.

**How to Enforce:**

Use `tach` (Python import linter):

```toml
[tool.tach]
modules = [
    "prompt_framework.providers",
    "prompt_framework.models",
    "prompt_framework.patterns",
    "prompt_framework.parsers",
    "prompt_framework.renderers",
    "prompt_framework.storage",
]

strict = true

[[tool.tach.constraints]]
type = "parent"
module = "prompt_framework.models"
parents = []  # models has no parents

[[tool.tach.constraints]]
type = "parent"
module = "prompt_framework.patterns"
parents = ["prompt_framework.models"]

[[tool.tach.constraints]]
type = "parent"
module = "prompt_framework.parsers"
parents = ["prompt_framework.models"]

# ... etc for all modules
```

Run `tach check` in CI to prevent violations.

### Contract 4: PatternSelector Auditability

**What It Means:** Tier selection is deterministic and auditable. Every tier choice comes with a rationale string explaining why.

**How to Enforce:**

```python
# CLI uses this
tier, rationale = PatternSelector().select(spec)
print(f"Selected {tier} because: {rationale}")

# Allows users to see why a tier was chosen
# and override if they disagree
```

---

## Domain Models (Complete Pydantic Definitions)

See the `models/` section above for the full Pydantic specs. Additional notes:

- All models use `validate_assignment=True` for runtime validation
- All models support JSON schema generation via `model_json_schema()`
- Enums are strings (not ints) for readability in output files
- Optional fields default to `None` or sensible empty collections

---

## Phased Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

**Deliverables:**
- `models/`: All Pydantic data structures
- `providers/`: Basic OpenAI provider implementation + unified interface
- `patterns/`: PatternSelector + Tier 1/2/3 pattern classes
- `patterns/rule_registry.py`: RuleBlockRegistry with built-in rule blocks
- `renderers/`: StandardPromptRenderer
- `storage/`: FileStorageBackend

**Acceptance Criteria:**
- `AgentSpec` → `FullPromptDesign` round-trip works for all three tiers
- `FullPromptDesign` → system prompt string works with zero logic
- All models pass Pydantic validation tests
- Import linter passes (no upward dependencies)
- Contract tests for renderer purity pass

**Milestones:**
- Day 3: models/ complete, type system validated
- Day 5: patterns/ complete, tier selection logic works
- Day 7: renderers/ complete, can serialize any FullPromptDesign
- Day 10: storage/ complete, can round-trip to filesystem
- Day 14: Full integration test (spec file → design → prompt)

---

### Phase 2: Parsing & Pattern Selection (Weeks 3-4)

**Deliverables:**
- `parsers/`: MarkdownSpecParser, SpecValidator
- `parsers/templates.py`: Markdown templates for `promptctl init-spec`
- PatternSelector enhancements: Criterion objects, better tier heuristics

**Acceptance Criteria:**
- Parse sample Markdown specs into valid AgentSpec objects
- Validation catches missing/invalid fields
- PatternSelector auditable (every selection has rationale)
- Templates match framework terminology (Task, Plan, Rule Blocks)

**Milestones:**
- Day 21: Parser reads Markdown, validates structure
- Day 28: Templates scaffold all required sections

---

### Phase 3: Evaluation Framework (Weeks 5-6)

**Deliverables:**
- `models/evaluation.py`: EvaluationMetrics, EvaluationResult, TestScenario schemas
- `agents/evaluator.py`: Stub EvaluatorAgent (single provider, hardcoded scenarios)
- Test scenario files (scenarios.md format)

**Acceptance Criteria:**
- Define what "good" prompt output looks like (metrics, scoring)
- EvaluatorAgent stub runs single test conversation and produces metrics
- Metrics align with rule block concepts (schema compliance, guardrails, etc.)
- Test scenarios are versioned and human-readable

**Milestones:**
- Day 35: EvaluationMetrics and EvaluationResult schemas finalized
- Day 42: EvaluatorAgent runs test with OpenAI, produces scores

---

### Phase 4: Design & Refinement Agents (Weeks 7-9)

**Deliverables:**
- `agents/design_agent.py`: Ingests AgentSpec + tier, outputs FullPromptDesign
- `agents/refinement_agent.py`: Ingests feedback/metrics, suggests diffs
- Anthropic & Gemini provider implementations
- Multi-provider EvaluatorAgent enhancements

**Acceptance Criteria:**
- DesignAgent produces valid FullPromptDesign objects (structure-validated)
- RefinementAgent outputs object-level diffs (not raw text blobs)
- Agents are stateless (state passed in/out)
- Evaluation works across OpenAI, Anthropic, Gemini

**Milestones:**
- Day 49: DesignAgent produces first-pass designs
- Day 56: RefinementAgent integrates evaluation feedback
- Day 63: Multi-provider evaluation works

---

### Phase 5a: CLI (Weeks 10-11)

**Deliverables:**
- `promptctl` CLI with commands:
  - `init-spec`: Scaffold new spec
  - `design`: Run DesignAgent, save result
  - `evaluate`: Run EvaluatorAgent(s), output report
- Help text, error messages, output formatting

**Acceptance Criteria:**
- CLI works end-to-end for all three tiers
- User can override tier selection
- Outputs are human-readable (formatted JSON, Markdown reports)
- Help documentation is complete

---

### Phase 5b: Integrations (Weeks 12-14)

**Deliverables (Conditional):**
- `storage/notion_backend.py`: NotionStorageBackend
- `api/main.py`: FastAPI service (optional)
- Documentation for extension points

**Acceptance Criteria:**
- Notion sync reads/writes pages containing designs
- FastAPI service exposes same CLI operations via HTTP
- Entry-points mechanism works for custom rule blocks

---

## Enforcement & Validation

### Import Linting

Use `tach` (Python import linter) to enforce layering:

```bash
pip install tach
tach check  # Validates imports against constraints
```

Configuration in `pyproject.toml` (see Contract 3 above).

### Contract Tests

Write unit tests that explicitly validate each contract:

```python
# tests/test_renderer_contract.py
def test_renderer_purity():
    """Renderer must output all parts as-is, no logic."""
    # Provide broken/invalid data; verify output includes it unchanged
    pass

def test_rule_block_symbolism():
    """Rule block refs must not resolve before render time."""
    # Build FullPromptDesign, verify resolved_rule_blocks is empty
    # Render, verify they're resolved only then
    pass

def test_tier_selection_auditability():
    """Every tier selection must include rationale."""
    # Call PatternSelector.select(), verify rationale is not empty
    pass
```

### Code Review Checklist

Before merging any PR:

- [ ] No upward import dependencies (ran `tach check`)
- [ ] If modifying `renderers/`, no conditional logic added
- [ ] If modifying `patterns/`, tier selection auditable (returns rationale)
- [ ] All new models in `models/` use Pydantic with validation
- [ ] Agents remain stateless (no instance state except config)
- [ ] New storage backends inherit from `StorageBackend` interface

### Continuous Integration

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint imports
        run: tach check
      - name: Run contract tests
        run: pytest tests/contracts/ -v
      - name: Type check
        run: mypy prompt_framework/
```

---

## Extensibility for Phase 5

### Storage Backend Interface

Any new backend inherits from `StorageBackend` and implements all abstract methods. Example:

```python
class CustomBackend(StorageBackend):
    async def write_spec(self, spec_id: str, spec: AgentSpec, owner: str):
        # Your implementation
        pass
    # ... etc
```

Backends are selected via config file or environment variable.

### Rule Block Registration (Entry Points)

Custom rule blocks via `pyproject.toml`:

```toml
[project.entry-points."prompt_framework.rule_blocks"]
company_rules = "my_company.rules:load_rule_blocks"
```

The entry point function returns `List[RuleBlock]`.

### Agent Capability Extension

Agents use `ProviderCapabilities` to declare requirements:

```python
if not provider.supports("function_calling"):
    # Use fallback implementation
    pass
```

New capabilities added to `ProviderCapabilities` enum; agents check before using.

---

## Glossary: Framework Terms → Code Entities

| Framework Concept | Code Entity | Location |
|---|---|---|
| **WHAT (outcomes, constraints)** | `TaskBlock` | `models/` |
| **HOW (execution steps, logic)** | `ExecutionPlanBlock` | `models/` |
| **DETAILS (schemas, formatting)** | `RuleBlock` | `models/` + registry |
| **Tier awareness** | `PromptTier` enum | `models/` |
| **Tier selection logic** | `PatternSelector` + `SelectionCriterion` | `patterns/` |
| **Tier 1/2/3 patterns** | `Tier1Pattern`, `Tier2Pattern`, `Tier3Pattern` classes | `patterns/` |
| **Complete design (resolved)** | `FullPromptDesign` | `models/` |
| **Input specification** | `AgentSpec` | `models/` |
| **Registry** | `RuleBlockRegistry` | `patterns/rule_registry` |
| **Rendering** | `PromptRenderer` interface + `StandardPromptRenderer` | `renderers/` |
| **Output (system prompt)** | `str` (rendered by `PromptRenderer`) | — |

---

## Open Questions & Future Decisions

1. **Version management:** How are rule block versions managed over time? Semantic versioning? Git tags?
2. **Feedback loop:** How does refinement feedback get encoded? Free-form text? Structured evaluation delta?
3. **Multi-language support:** Should rule blocks support multiple languages (French, Spanish)? Entry point per language?
4. **Caching:** Should PromptDesign outputs be cached? Where (filesystem, Redis)?
5. **Audit trail:** Should all design iterations be persisted? (Append-only log or versioning?)
6. **Notion schema:** If Notion sync is added, what Notion properties map to AgentSpec fields?

---

## Summary

This architecture encodes the orthogonal prompt design methodology into enforceable code boundaries. Success requires strict adherence to layering contracts (especially renderer purity, reference symbolism, and one-way dependencies). The phased plan de-risks by building evaluation early, before agents. Extensibility is designed in from the start (entry-points for rule blocks, pluggable storage backends) without complicating Phase 1.

The critical path to production is: **Phase 1 foundation → Phase 2 parsing → Phase 3 evaluation schema → Phase 4 agents → Phase 5 CLI**. Any deviation (e.g., building agents before evaluation is defined) will require rework.

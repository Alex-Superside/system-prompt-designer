# Python Best Practices Guide for AI-Assisted Development

## 🎯 Purpose
This document serves as coding standards for AI agents to ensure consistent, maintainable, and production-ready Python code. Follow these rules when writing, reviewing, or refactoring Python code.

## 📋 Core Principles

### 1. **Single Responsibility Principle**
Each function should do exactly one thing.

```python
# ❌ WRONG - Multiple responsibilities
def discover_and_parse_patterns(client, project_names):
    prompt = build_prompt(project_names)  # Responsibility 1: Prompt building
    response = client.create(prompt)      # Responsibility 2: API call
    data = json.loads(response)           # Responsibility 3: JSON parsing
    return validate_data(data)            # Responsibility 4: Validation

# ✅ CORRECT - Single responsibilities
def build_analysis_prompt(project_names: list[str]) -> str:
    """Build prompt for pattern analysis."""
    
def call_openai_api(client: OpenAI, prompt: str) -> str:
    """Make API call with error handling."""
    
def parse_json_response(response: str) -> dict:
    """Parse and validate JSON response."""
```

### 2. **Function Length Limit**
Functions must be **≤ 20 lines**. If longer, break into smaller functions.

```python
# ❌ WRONG - 65 line function
def discover_project_patterns(client, project_names):
    # ... 65 lines of mixed concerns

# ✅ CORRECT - Composed of small functions  
def discover_project_patterns(project_names: list[str]) -> dict:
    """Orchestrate pattern discovery workflow."""
    prompt = build_analysis_prompt(project_names)
    response = call_openai_api(get_client(), prompt)
    return parse_pattern_response(response)
```

### 3. **No Hardcoded Values**
Extract all magic numbers, strings, and configuration to constants or config files.

```python
# ❌ WRONG - Hardcoded values scattered
model="gpt-4"
max_tokens=2000
temperature=0.1
f"stage_3_recurrent_analysis_{company_id}.json"

# ✅ CORRECT - Centralized configuration
@dataclass
class OpenAIConfig:
    MODEL: str = "gpt-4"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.1

class FilePatterns:
    STAGE_3_OUTPUT = "stage_3_recurrent_analysis_{company_id}.json"
```

### 4. **Externalize Complex Templates**
Never embed long strings or prompts directly in code.

```python
# ❌ WRONG - 40+ line prompt embedded in function
def build_prompt(names):
    prompt = f"""
    Analyze the following list of project names and identify recurring patterns...
    [40+ more lines]
    Return your analysis as a JSON object with this structure:
    {{
        "recurring_patterns": [...]
    }}
    """

# ✅ CORRECT - External template management
class PromptTemplates:
    @staticmethod
    def load_template(name: str) -> str:
        return (Path("templates") / f"{name}.txt").read_text()
    
    PATTERN_ANALYSIS = load_template("pattern_analysis")

def build_analysis_prompt(project_names: list[str]) -> str:
    return PromptTemplates.PATTERN_ANALYSIS.format(
        project_list=format_project_names(project_names),
        total_projects=len(project_names)
    )
```

### 5. **String Formatting Consistency**
Use consistent string formatting strategy based on complexity.

```python
# ✅ RULES:
# Simple (1-2 vars) → f-strings
message = f"Processing {count} items for {user}"

# Complex templates → .format()
template = "Welcome {name}! You have {count} items in {category}".format(
    name=name, count=count, category=category
)

# ❌ AVOID - f-strings with many escaped braces
confusing = f"JSON: {{ \"count\": {count}, \"data\": {{ \"nested\": {value} }} }}"

# ✅ CORRECT - Use .format() or Template for complex cases
json_template = '{{ "count": {count}, "data": {{ "nested": {value} }} }}'
result = json_template.format(count=count, value=value)
```

### 6. **Specific Exception Handling**
Never use broad `except Exception` unless absolutely necessary.

```python
# ❌ WRONG - Too broad
try:
    result = risky_operation()
except Exception as e:  # Catches everything
    logger.error(f"Error: {e}")

# ✅ CORRECT - Specific exceptions
try:
    result = api_call()
except requests.ConnectionError as e:
    logger.error(f"API connection failed: {e}")
except requests.Timeout as e:
    logger.error(f"API timeout: {e}")  
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
```

### 7. **Input Validation**
Always validate inputs at function boundaries.

```python
# ❌ WRONG - No validation
def process_projects(projects_data):
    for project in projects_data:
        name = project['project_name']  # Could KeyError or None

# ✅ CORRECT - Defensive validation
def process_projects(projects_data: list[dict[str, Any]]) -> list[str]:
    """Process project data with validation."""
    if not isinstance(projects_data, list):
        raise TypeError("projects_data must be a list")
    
    if not projects_data:
        raise ValueError("projects_data cannot be empty")
    
    validated_names = []
    for i, project in enumerate(projects_data):
        if not isinstance(project, dict):
            raise TypeError(f"Project {i} must be a dictionary")
            
        name = project.get('project_name', '').strip()
        if not name:
            raise ValueError(f"Project {i} missing valid name")
            
        validated_names.append(name)
    
    return validated_names
```

### 8. **File Operations Standards**
Always specify encoding and handle file operations safely.

```python
# ❌ WRONG - No encoding, no error handling
with open(filename) as f:
    data = json.load(f)

# ✅ CORRECT - Explicit encoding and error handling
def load_json_file(filepath: Path) -> dict:
    """Load JSON file with proper error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Required file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e}")
    except PermissionError:
        raise PermissionError(f"Cannot read file: {filepath}")
```

### 9. **Pure vs Impure Function Separation**
Separate business logic (pure) from side effects (impure).

```python
# ❌ WRONG - Mixed pure logic with side effects
def calculate_patterns(project_names):
    logger.info("Starting analysis")  # Side effect
    prompt = build_prompt(project_names)  # Pure logic
    response = api_call(prompt)  # Side effect
    result = parse_response(response)  # Pure logic
    logger.info("Analysis complete")  # Side effect
    return result

# ✅ CORRECT - Separate pure and impure
def build_analysis_prompt(project_names: list[str]) -> str:
    """Pure function - no side effects."""
    return create_prompt_template().format(names=project_names)

def analyze_patterns_with_api(project_names: list[str]) -> dict:
    """Impure function - handles all side effects."""
    logger.info("Starting pattern analysis")
    
    prompt = build_analysis_prompt(project_names)  # Pure
    response = call_openai_api(prompt)  # Side effect
    result = parse_pattern_response(response)  # Pure
    
    logger.info("Pattern analysis complete")
    return result
```

### 10. **Type Hints Precision**
Use specific types instead of `Any` whenever possible.

```python
# ❌ WRONG - Too generic
def process_data(data: Any) -> Any:
    return transform(data)

# ✅ CORRECT - Specific types
from typing import TypedDict

class ProjectData(TypedDict):
    project_name: str
    project_id: int
    created_date: str

class PatternResult(TypedDict):
    pattern_name: str
    confidence: Literal['high', 'medium', 'low']
    project_indices: list[int]

def analyze_project_patterns(
    projects: list[ProjectData]
) -> list[PatternResult]:
    """Analyze projects with specific type contracts."""
```

### 11. **Configuration Management**
Centralize all configuration in dedicated classes or files.

```python
# ✅ CORRECT - Centralized config
@dataclass
class AppConfig:
    # API Configuration
    OPENAI_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.1
    API_TIMEOUT: int = 30
    
    # File Paths
    DATA_DIR: Path = Path("data")
    TEMPLATE_DIR: Path = Path("templates")
    
    # Processing Limits
    MAX_PROJECTS_PER_BATCH: int = 100
    MIN_PATTERN_SIZE: int = 2
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables."""
        return cls(
            OPENAI_MODEL=os.getenv('OPENAI_MODEL', cls.OPENAI_MODEL),
            MAX_TOKENS=int(os.getenv('MAX_TOKENS', cls.MAX_TOKENS)),
            # ... etc
        )

# Usage
config = AppConfig.from_env()
```

### 12. **Error Messages with Context**
Provide actionable error messages with context.

```python
# ❌ WRONG - Vague errors
raise ValueError("Invalid data")
raise FileNotFoundError("File not found")

# ✅ CORRECT - Specific, actionable errors
raise ValueError(
    f"Project data validation failed: {len(invalid_projects)} projects "
    f"missing required 'project_name' field. First invalid project at index {first_invalid_idx}"
)

raise FileNotFoundError(
    f"Required input file not found: {expected_file}\n"
    f"Run 'python stage_2_preprocessing.py {company_id}' first to generate this file."
)
```

### 13. **Dependency Injection for Testability**
Make external dependencies injectable for testing.

```python
# ❌ WRONG - Hard dependencies
def analyze_patterns(project_names):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Hard dependency
    response = client.chat.completions.create(...)

# ✅ CORRECT - Dependency injection
def analyze_patterns(
    project_names: list[str], 
    client: OpenAI,
    config: OpenAIConfig = OpenAIConfig()
) -> dict:
    """Analyze patterns with injected dependencies."""
    prompt = build_prompt(project_names)
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE
    )
    return parse_response(response)
```

### 14. **Resource Management & Cleanup**
Always handle resource cleanup properly.

```python
# ✅ CORRECT - Context managers for resources
@contextmanager
def openai_client(api_key: str) -> Iterator[OpenAI]:
    """Context manager for OpenAI client."""
    client = OpenAI(api_key=api_key)
    try:
        yield client
    finally:
        # Cleanup if needed
        pass

def analyze_with_managed_client(project_names: list[str]) -> dict:
    with openai_client(get_api_key()) as client:
        return analyze_patterns(project_names, client)
```

### 15. **Consistent Error Handling Placement**
Use layered error handling strategy based on error type.

```python
# ✅ LAYER 1: Input validation - EARLY (guard clauses)
def process_data(data: list[dict]) -> ProcessedData:
    # Input validation - fail fast
    if not isinstance(data, list):
        raise TypeError("data must be a list")
    if not data:
        raise ValueError("data cannot be empty")
    if not all(isinstance(item, dict) for item in data):
        raise TypeError("all items must be dictionaries")

# ✅ LAYER 2: External operations - SPECIFIC try/catch
    try:
        api_result = call_external_api(data)
    except (ConnectionError, TimeoutError) as e:
        raise ExternalServiceError(f"API call failed: {e}") from e
    except json.JSONDecodeError as e:
        raise DataProcessingError(f"Invalid API response: {e}") from e

# ✅ LAYER 3: Business logic - should be safe after validation
    return transform_validated_data(api_result)

# ❌ WRONG - Mixed placement, catch-all at end
def bad_function(data):
    try:
        if not data:  # Should be early guard clause
            return None
        result = call_api(data)
        parsed = json.loads(result)
        return process(parsed)
    except Exception as e:  # Too broad, too late
        logger.error(f"Something failed: {e}")
        return None
```

**Error Handling Rules:**
- **EARLY**: Input validation, preconditions, configuration checks
- **SPECIFIC**: External API calls, file I/O, data parsing
- **NEVER**: Broad `except Exception` catching mixed concerns

## 🚨 AI Agent Enforcement Rules

### **MANDATORY CHECKS**
1. ✅ Functions ≤ 20 lines
2. ✅ No hardcoded strings/numbers in business logic  
3. ✅ All inputs validated at function entry (EARLY)
4. ✅ Specific exception handling (no bare `except`)
5. ✅ External operations wrapped in specific try/catch
6. ✅ File operations specify encoding
7. ✅ Type hints use specific types over `Any`
8. ✅ Templates externalized from code
9. ✅ Single responsibility per function
10. ✅ Consistent error handling placement

### **REFACTORING TRIGGERS**
- Function > 20 lines → **Split immediately**
- String > 10 lines in code → **Extract to template** 
- More than 2 hardcoded values → **Create config class**
- `except Exception:` → **Use specific exceptions**
- Mixed pure/impure logic → **Separate concerns**

### **CODE REVIEW CHECKLIST**
- [ ] Can each function be unit tested in isolation?
- [ ] Are all magic values extracted to constants?
- [ ] Do error messages provide actionable guidance?
- [ ] Are complex templates externalized?
- [ ] Is string formatting consistent throughout?
- [ ] Are external dependencies injected, not hardcoded?

### 16. **Avoid Over-Refactoring - The "Goldilocks Zone"**
Balance theoretical purity with practical maintainability based on business context.

```python
# ❌ OVER-ENGINEERED - Too abstract for simple case
class SystemPromptManager:
    def __init__(self, prompt_registry: PromptRegistry):
        self.registry = prompt_registry
    
    def get_pattern_analysis_prompt(self) -> SystemPrompt:
        return self.registry.load_prompt(PromptType.PATTERN_ANALYSIS)
# 20+ lines to manage a simple constant string

# ✅ PRAGMATIC - Simple and clear for static content
@dataclass
class LLMConfig:
    model: str = "gpt-4"
    SYSTEM_PROMPT: str = "You are an expert at identifying business patterns..."
# Configurable but not over-engineered

# ✅ FULL ABSTRACTION - When complexity justifies it
class PromptManager:
    """Use when multiple prompts, frequent changes, role separation needed"""
    def load_template(self, template_id: str) -> str:
        return (Path("prompts") / f"{template_id}.txt").read_text()
```

**Refactoring Decision Framework:**
- **Frequency Test**: Refactor if changes >monthly, keep simple if static for months
- **Complexity Test**: Refactor if validation/logic needed, keep simple for constants  
- **Team Test**: Refactor if multiple people modify, keep simple for single maintainer
- **Business Value Test**: Refactor if directly impacts business logic, keep simple for display text

### 17. **Role Separation at Team Level**
Technical decisions should enable role-based workflows, not just code purity.

```python
# SCENARIO: Prompt Designer + Developer team
# ❌ WRONG - Forces prompt expert to modify code
def call_llm_api(...):
    system_prompt = "You are an expert..."  # Prompt designer can't touch this!
    
# ✅ CORRECT - Enables role separation  
def call_llm_api(...):
    system_prompt = PromptManager.get_system_prompt("pattern_analysis")
    # Prompt designer owns prompt files, developer owns code logic

# DECISION MATRIX:
# Static content + Single role → Keep in code
# Iterative content + Multiple roles → External files
# Expert domain knowledge → Let experts control their domain
```

**Role Separation Rules:**
- **Prompt Designers** should control prompt content without code changes
- **Data Scientists** should control evaluation datasets independently  
- **Developers** should focus on stable infrastructure, not domain content
- **Context Engineers** should configure data injection without API changes

### 18. **AI Agentic System Architecture**
Modern AI systems need rapid iteration on three core components.

```python
# THE AI ITERATION TRINITY - Components that need fast-paced iteration:

# 1. PROMPTS (System + User) - Daily/hourly changes
@dataclass  
class AIPromptConfig:
    system_prompts_dir: Path = Path("ai_components/prompts/system")
    user_templates_dir: Path = Path("ai_components/prompts/user")

class PromptRegistry:
    def get_system_prompt(self, prompt_id: str) -> str:
        """Load from YAML files - designer controlled"""
        return self._load_prompt_yaml(prompt_id)

# 2. EVALUATION DATASETS - Constantly evolving test cases
class EvalDatasetManager:
    def load_dataset(self, dataset_id: str) -> EvalDataset:
        """Load from CSV/JSON - data scientist controlled"""
        return self._load_eval_cases(dataset_id)

# 3. CONTEXT INJECTION - Complex pipelines needing experimentation  
class ContextInjectionManager:
    def inject_context(self, prompt: str, pipeline_id: str) -> str:
        """Execute pipeline from config - context engineer controlled"""
        pipeline = self._load_pipeline_config(pipeline_id)
        return self._execute_pipeline(prompt, pipeline)

# ORCHESTRATOR - Developer maintains, AI experts control behavior
class AIAgentOrchestrator:
    def __init__(self, prompts: PromptRegistry, evals: EvalDatasetManager, 
                 context: ContextInjectionManager):
        # Dependency injection enables role separation
        self.prompts = prompts
        self.evals = evals  
        self.context = context
    
    def execute_agent_task(self, task_id: str, input_data: dict) -> dict:
        """Stable code - AI behavior controlled by external components"""
        system_prompt = self.prompts.get_system_prompt(f"{task_id}_system")
        user_prompt = self.context.inject_context(template, "default_pipeline") 
        return self._call_llm(system_prompt, user_prompt)
```

**AI Architecture Principles:**
- **Separate AI behavior from code logic** - behavior changes shouldn't require deployments
- **Enable domain experts** - let AI designers control AI components
- **Fast iteration cycles** - minutes/hours for AI changes vs days for code changes
- **Stable infrastructure** - developers focus on reliable systems, not AI experimentation

### 19. **Progressive Enhancement Strategy**
Start simple, add complexity only when pain points justify it.

```python
# VERSION 1: Simple and working (ship this first)
def analyze_patterns_v1(project_names: list[str]) -> dict:
    """Simple version - hardcoded but functional"""
    prompt = f"Analyze these projects: {project_names}"
    return call_openai_api(prompt)

# VERSION 2: Add configuration when needed  
def analyze_patterns_v2(project_names: list[str], config: LLMConfig) -> dict:
    """Enhanced when requirements change"""
    prompt = config.PROMPT_TEMPLATE.format(projects=project_names)
    return call_openai_api(prompt, config)

# VERSION 3: Full abstraction when complexity justifies it
def analyze_patterns_v3(input_data: dict, agent_config: AgentConfig) -> dict:
    """Full abstraction when multiple use cases emerge"""
    orchestrator = AIAgentOrchestrator.from_config(agent_config)
    return orchestrator.execute_task("pattern_analysis", input_data)
```

**Enhancement Decision Points:**
- **V1 → V2**: When configuration becomes necessary (multiple environments)
- **V2 → V3**: When multiple similar functions appear (DRY violation)
- **V3 → Full System**: When role separation becomes necessary (team scaling)

### 20. **Business Context Drives Technical Decisions**
Architecture should solve real workflow problems, not theoretical purity.

```python
# EXAMPLE: System prompt placement decision

# CONTEXT 1: Single developer, static prompt
class SimpleConfig:
    SYSTEM_PROMPT = "You are an expert..."  # ✅ Keep it simple

# CONTEXT 2: Prompt designer + developer team, iterative prompts  
class TeamConfig:
    def get_system_prompt(self, prompt_id: str) -> str:  # ✅ Enable role separation
        return PromptManager.load_template(prompt_id)

# CONTEXT 3: Multiple agents, complex prompt logic
class EnterpriseConfig:
    def __init__(self, prompt_registry: PromptRegistry):  # ✅ Full abstraction
        self.prompts = prompt_registry
```

**Business Context Questions:**
- **Who modifies this component?** (Single person vs multiple roles)
- **How often does it change?** (Static vs iterative)
- **What's the cost of deployment?** (Minutes vs days)
- **What expertise is required?** (Code knowledge vs domain knowledge)
- **What are the failure modes?** (Development velocity vs system reliability)

## 🚨 AI Agent Enforcement Rules

### **MANDATORY CHECKS**
1. ✅ Functions ≤ 20 lines
2. ✅ No hardcoded strings/numbers in business logic  
3. ✅ All inputs validated at function entry (EARLY)
4. ✅ Specific exception handling (no bare `except`)
5. ✅ External operations wrapped in specific try/catch
6. ✅ File operations specify encoding
7. ✅ Type hints use specific types over `Any`
8. ✅ Templates externalized from code
9. ✅ Single responsibility per function
10. ✅ Consistent error handling placement
11. ✅ **Business context justifies refactoring level**
12. ✅ **Role separation enables team workflow efficiency**
13. ✅ **AI components externalized for rapid iteration**

### **REFACTORING TRIGGERS**
- Function > 20 lines → **Split immediately**
- String > 10 lines in code → **Extract to template** 
- More than 2 hardcoded values → **Create config class**
- `except Exception:` → **Use specific exceptions**
- Mixed pure/impure logic → **Separate concerns**
- **Multiple roles editing same component → External files**
- **AI behavior changes requiring code deployment → Externalize AI components**
- **Frequent iteration blocked by code review cycle → Designer independence pattern**

### **CODE REVIEW CHECKLIST**
- [ ] Can each function be unit tested in isolation?
- [ ] Are all magic values extracted to constants?
- [ ] Do error messages provide actionable guidance?
- [ ] Are complex templates externalized?
- [ ] Is string formatting consistent throughout?
- [ ] Are external dependencies injected, not hardcoded?
- [ ] **Does the refactoring level match the business context?**
- [ ] **Can domain experts modify their components without developer help?**
- [ ] **Are fast-iteration components (prompts, eval data, context) externalized?**

This guide ensures code is maintainable, testable, and production-ready while enabling efficient team workflows and rapid AI iteration cycles.
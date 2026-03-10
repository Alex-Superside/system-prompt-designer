# GPT-5.4 Migration Guide: Phase 1

**Status:** ✅ Implemented & Tested
**Test Coverage:** 323 tests passing | 90% overall coverage
**Date:** 2026-03-06

---

## What Changed

Phase 1 of the GPT-5.4 migration now routes **GPT-5.x models through the Responses API** so the CLI can control both `reasoning.effort` and `text.verbosity` using official OpenAI request fields. Non-GPT-5 models remain on Chat Completions for backward compatibility.

### Summary of Changes

| Component | Change | Impact |
|-----------|--------|--------|
| **Default Model** | `gpt-4o` → `gpt-5-mini` | Faster, cheaper reasoning |
| **Default Max Tokens** | 2000 → 1500 | 25% token reduction for gpt-5.x |
| **New Feature: Reasoning Effort** | Added `--verbosity [none\|low\|medium\|high\|xhigh]` | Control GPT-5 reasoning depth |
| **New Feature: Output Verbosity** | Added `--output-verbosity [low\|medium\|high]` | Control GPT-5 response length/detail |
| **New Feature: Model Override** | Added `--model <name>` flag | Support gpt-5.4-pro, gpt-5-mini, etc. |
| **Environment Variables** | Added `OPENAI_REASONING_EFFORT`, `OPENAI_TEXT_VERBOSITY`, kept `OPENAI_VERBOSITY` alias | Externalized defaults |

---

## How to Use

### Basic Usage (No Changes Needed)

Existing commands work exactly as before:

```bash
promptctl design spec.md              # Now uses gpt-5.4 instead of gpt-4o
promptctl run my-agent --message "test"
promptctl refine my-agent --feedback "add structure"
```

### New Flags: Model Selection

Use `--model` to override the default (gpt-5.4):

```bash
# Use gpt-5.4-pro (professional variant)
promptctl design spec.md --model gpt-5.4-pro

# Fall back to gpt-4o
promptctl design spec.md --model gpt-4o

# Use gpt-5-mini (lightweight)
promptctl design spec.md --model gpt-5-mini

# Apply model to all commands
promptctl run my-agent --message "test" --model gpt-5.4-pro
promptctl refine my-agent --feedback "..." --model gpt-5.4-pro
promptctl audit my-agent --model gpt-5.4-pro
```

### New Flags: Reasoning Effort (GPT-5.x Only)

Use `--verbosity` to control reasoning depth for gpt-5.x models:

```bash
# Lowest-latency reasoning
promptctl design spec.md --verbosity none

# Fast reasoning
promptctl design spec.md --verbosity low

# Balanced reasoning (default)
promptctl design spec.md --verbosity medium

# Deep reasoning (slower, better results)
promptctl design spec.md --verbosity high

# Maximum reasoning for difficult tasks
promptctl design spec.md --verbosity xhigh
```

### New Flags: Output Verbosity (GPT-5.x Only)

Use `--output-verbosity` to control how detailed the final response is:

```bash
promptctl design spec.md --output-verbosity low
promptctl design spec.md --output-verbosity medium
promptctl design spec.md --output-verbosity high
```

### Environment Configuration

Set defaults in `.env` or `.env.local`:

```bash
# Set default model to gpt-5.4-pro
OPENAI_MODEL=gpt-5.4-pro

# Set default reasoning effort to high
OPENAI_REASONING_EFFORT=high

# Set default output verbosity to concise
OPENAI_TEXT_VERBOSITY=low

# Backward-compatible alias for reasoning effort
OPENAI_VERBOSITY=high

# Override max tokens (normally auto-selected by model)
OPENAI_MAX_TOKENS=2000
```

**Load Order:**
1. Command-line flags (highest priority)
2. Environment variables
3. Hardcoded defaults (gpt-5-mini, medium reasoning, medium output verbosity, 1500 tokens)

---

## Model-Specific Defaults

### Token Limits (Auto-Selected)

| Model | Max Tokens | Notes |
|-------|-----------|-------|
| gpt-5-mini | 1500 | Default; cost-efficient reasoning |
| gpt-5.4 | 1500 | Optimized for reasoning |
| gpt-5.4-pro | 1500 | Higher capacity variant |
| gpt-5-mini | 1500 | Lightweight variant |
| gpt-4o | 2000 | Previous generation |
| Other | 2000 | Conservative default |

Override with `OPENAI_MAX_TOKENS=<number>` if needed.

### Reasoning Effort Application

**Applied to (gpt-5.x models):**
- gpt-5.4
- gpt-5.4-pro
- gpt-5-mini

**Ignored for (gpt-4.x models):**
- gpt-4o
- gpt-4-turbo
- Other gpt-4 variants

---

## Backward Compatibility

### Your Existing Designs Still Work

Existing design JSON files, spec Markdown files, and rendered prompts require **no changes**:

```bash
# Load an old design created with gpt-4o
promptctl run my-old-agent --message "test"

# Refine it with the new default (gpt-5.4)
promptctl refine my-old-agent --feedback "improve..."

# The design.json and system.md are completely compatible
```

### Explicit Fallback to GPT-4.x

If you need to keep using gpt-4o:

```bash
# Option 1: Command-line flag (per command)
promptctl design spec.md --model gpt-4o

# Option 2: Environment variable (all commands)
export OPENAI_MODEL=gpt-4o

# Option 3: .env file (project-level)
echo "OPENAI_MODEL=gpt-4o" >> .env
```

---

## What's Included in Phase 1

### Code Changes

**`prompt_design_system/config.py`**
- Added `ReasoningEffort` enum (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `XHIGH`)
- Added `VerbosityLevel` enum (`LOW`, `MEDIUM`, `HIGH`)
- Updated `LLMConfig` defaults: model → gpt-5-mini, max_tokens → 1500
- Added `reasoning_effort` and `text_verbosity` fields to `LLMConfig`
- Added `get_max_tokens_for_model()` helper for model-specific defaults
- Enhanced `from_env()` to load reasoning effort, output verbosity, and auto-select max_tokens

**`prompt_design_system/providers.py`**
- Added `reasoning_effort` and `text_verbosity` parameters to `OpenAIProvider.__init__()`
- Routed GPT-5.x calls to `client.responses.create(...)`
- Updated both `generate()` and `generate_with_system()` to normalize Responses API and Chat Completions responses
- GPT-5.x now sends `reasoning={"effort": ...}` and `text={"verbosity": ...}`; gpt-4.x stays on Chat Completions

**`prompt_design_system/cli.py`**
- Added `--model` flag to design, refine, run, audit commands
- Added `--verbosity` flag to design, refine, run, audit commands
- Added `--output-verbosity` flag to design, refine, run, audit commands
- Updated `_resolve_llm_client()` to accept and pass through model, reasoning effort, and output verbosity
- Added validation for reasoning effort and output verbosity values with helpful error messages

### Tests Added

**`tests/test_config.py`** (30 new tests)
- VerbosityLevel enum creation and string conversion
- LLMConfig defaults and custom initialization
- Model-specific max_tokens logic
- Environment variable loading and fallback behavior

**`tests/test_providers.py`** (12 new tests)
- Reasoning effort included for gpt-5.x models
- Reasoning effort omitted for gpt-4.x models
- Model variant support (gpt-5.4, gpt-5.4-pro, gpt-5-mini)
- Updated default model assertion (gpt-4o → gpt-5.4)

### Documentation Updates

**`README.md`**
- Added "Model and Verbosity Control" section
- Documented all supported models
- Explained reasoning effort levels
- Updated test count (323 tests, 90% coverage)

**`WORKBENCH_DESIGN.md`**
- Updated command documentation with `--model` and `--verbosity` flags
- Added "Model and Verbosity Control" section
- Explained environment variable configuration
- Documented that `--verbosity` is gpt-5.x-only

---

## Testing & Validation

### Test Suite Results

```
323 tests passing
90% code coverage
- providers.py: 100% coverage
- config.py: 97% coverage
- models.py: 100% coverage
- storage.py: 100% coverage
- cli.py: 80% coverage
```

### Key Test Cases

✅ Default model is gpt-5-mini
✅ Reasoning effort passed only for gpt-5.x models
✅ Reasoning effort omitted for gpt-4.x models
✅ Model-specific token limits auto-selected
✅ Environment variables override defaults
✅ Command-line flags override everything
✅ Invalid verbosity rejected with helpful message
✅ All model variants accepted (gpt-5.4-pro, gpt-5-mini, etc.)

---

## Troubleshooting

### "Invalid verbosity level 'xyz'"

**Symptom:** Command fails with verbosity validation error

**Fix:** Use one of: `low`, `medium`, `high`

```bash
# ❌ Wrong
promptctl design spec.md --verbosity deep

# ✅ Correct
promptctl design spec.md --verbosity high
```

### Reasoning effort parameter not being passed

**Symptom:** Using gpt-5.4 but reasoning_effort doesn't appear in API logs

**Cause:** You're using a gpt-4.x model by accident

**Fix:** Verify the model you're using:

```bash
# Check which model is actually running
OPENAI_MODEL=gpt-5.4 promptctl design spec.md --verbose

# Or explicitly override
promptctl design spec.md --model gpt-5.4 --verbose
```

### Old designs using different API parameters

**Symptom:** "My old design was created with gpt-4o, will it break?"

**Answer:** No. Designs are independent of the model used to create them. Run the old design with any model:

```bash
promptctl run my-old-agent --message "test" --model gpt-4o   # Still works
promptctl run my-old-agent --message "test" --model gpt-5.4   # Also works
```

---

## Next Steps (Phase 2 & 3 - Planned)

### Phase 2: Model Variants & Project-Level Config
- Support saving preferred model per project (projects/<name>/.promptctl-config)
- CLI: `promptctl config set --model gpt-5.4-pro`
- Auto-apply saved model to design/refine/audit commands

### Phase 3: Cost Tracking & Analytics
- Token usage analytics: `promptctl stats`
- Cost estimation by model
- Historical design costs

---

## FAQ

### Q: Will my existing designs break?

**A:** No. Designs are model-agnostic. A design created with gpt-4o works with gpt-5.4 and vice versa.

### Q: Should I upgrade all my models to gpt-5.4?

**A:** Yes, unless you have a specific reason to use gpt-4o (e.g., cost constraints, API availability).

### Q: Can I use gpt-5.4-pro and gpt-5-mini?

**A:** Yes. Use `--model gpt-5.4-pro` or `--model gpt-5-mini` on any command.

### Q: What's the difference between verbosity levels?

- **low:** Fast responses, minimal reasoning (good for simple tasks)
- **medium:** Balanced (default for most use cases)
- **high:** Slow responses, deep reasoning (good for complex analysis)

### Q: Does verbosity affect token costs?

**A:** Potentially yes; higher verbosity may produce longer reasoning chains, using more tokens. This depends on the task and model.

### Q: What if I'm offline or without OPENAI_API_KEY?

**A:** The tool falls back to heuristic-only mode (no LLM). Designs still work using the framework rules. See README.md for details.

---

## Support

For issues or questions:
1. Check the [README.md](README.md) for setup and installation
2. Check [WORKBENCH_DESIGN.md](WORKBENCH_DESIGN.md) for command reference
3. Review test coverage in `tests/test_config.py` and `tests/test_providers.py` for implementation details
4. Run `promptctl design --help` for CLI documentation

---

## Summary

Phase 1 successfully migrates the prompt design workbench to GPT-5.4 while maintaining full backward compatibility. Users can upgrade gradually, test with flags, and fall back to gpt-4o if needed. The next phases will add per-project model defaults and cost analytics.

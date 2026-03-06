# Non-Reasoning Model Design

## Definition

Prompt design patterns optimized for models that don't perform complex reasoning—mini models, fast models, or models with reduced reasoning capability.

## Why This Matters

**Reasoning models** (Claude 4, o1, GPT > 5.0):
- Can infer rules from examples
- Handle ambiguous instructions
- "Figure out" the right approach
- More forgiving of implicit rules

**Non-reasoning models** (Claude Haiku, smaller fine-tuned models, GPT <= 4.1):
- Need explicit, detailed rules
- Struggle with inference
- Require unambiguous instructions
- Better with structured inputs/outputs

## Design Principle: Explicit > Implicit

### ❌ Implicit Rule (Fails with Non-Reasoning)

```
Task: "Generate helpful customer responses"

→ Model must infer:
   - What is "helpful"?
   - What tone?
   - What scope?
   - What format?

→ Non-reasoning model guesses wrong
```

### ✅ Explicit Rule (Works with Non-Reasoning)

```
Task: "Generate customer responses that are polite, concise,
and address one issue per response."

Rule Block: "Tone Rules - Always polite, never sarcastic.
One issue per response. Max 3 sentences."

→ Model has clear guidance
→ Non-reasoning model can execute
```

## Design Patterns for Non-Reasoning Models

### Pattern 1: Hyper-Explicit Rule Blocks

**Normal Rule Block:**
```
Output Format: "Brief intro + bullet list"
```

**Non-Reasoning Rule Block:**
```
Output Format Rules:
1. Start with 1-2 sentence intro (concise overview)
2. Follow with bulleted list of items
3. Each bullet is 1 sentence max
4. No sub-bullets
5. No additional text after list
6. Use only plain text, no bold or italics
```

### Pattern 2: Narrow Procedural Steps

**Normal Plan:**
```xml
<step>
  <action_name>generate_response</action_name>
  <description>Generate a helpful response</description>
</step>
```

**Non-Reasoning Plan:**
```xml
<step>
  <action_name>identify_issue_type</action_name>
  <description>Classify user issue as: billing, technical, shipping,
  other. If unclear, ask for clarification.</description>
</step>

<step>
  <action_name>select_response_template</action_name>
  <description>Choose template from Response Template Rules matching
  issue type.</description>
</step>

<step>
  <action_name>fill_template</action_name>
  <description>Fill template with specific details from user message.
  Do not deviate from template structure.</description>
</step>
```

### Pattern 3: Schema-First Output

**Without schema:** Model infers best format

**With schema:** Model must follow exact structure

```json
{
  "issue_type": "string (billing|technical|shipping|other)",
  "response": "string (response text)",
  "followup_question": "string or null (optional)"
}
```

**Non-reasoning models** perform better with explicit schema.

### Pattern 4: Enumerated Choices

**Implicit:** "Choose an appropriate action"

**Explicit:** "Choose one:
1. Answer directly
2. Ask for clarification
3. Escalate to human"

Map each choice to specific action → no inference needed.

## Tier Implications

### Tier 1: Risky for Non-Reasoning

```
Task only: "Be creative and helpful"

→ Model must infer everything
→ Results are unpredictable
→ Not recommended for non-reasoning
```

### Tier 2: Acceptable with Care

```
Task + Plan: Clear steps, but implicit tone/formatting

→ Better than Tier 1
→ Still relies on inference
→ Watch for inconsistency
```

### Tier 3: Best for Non-Reasoning

```
Task + Plan + Rule Blocks: Explicit everything

→ Model doesn't infer
→ Follows explicit rules
→ Consistent output
→ Recommended for non-reasoning
```

## Real-World Example: Brief-Writing Agent on Haiku

**Challenge:** Brief-writing agent uses [[11-Brief-Writing-Agent]] (Tier 3) on Claude Haiku (non-reasoning).

**Solution:**

1. **Hyper-explicit citation rules**
   - Not: "Mark citations appropriately"
   - Yes: "Wrap text in `<mark data-type="citation">`, immediately follow with `<sup>[number]</sup>`"

2. **Step-by-step validation**
   - Not: "Ensure citations are correct"
   - Yes: "Check each citation has matching `<mark>` and `<sup>`. Check numbers are 1, 2, 3..."

3. **Template-based generation**
   - Not: "Generate sections as needed"
   - Yes: "Generate these sections in order: [section names], using [template] for each"

4. **No examples in Task/Plan**
   - Minimal examples in Rule Blocks only
   - Examples show exact syntax, not creative variation

## Testing for Non-Reasoning Readiness

**Checklist:**

- [ ] Are all rules explicit (not inferred)?
- [ ] Can Plan steps be executed mechanically?
- [ ] Are all outputs schema-defined?
- [ ] Are examples in Rule Blocks only?
- [ ] Could a non-technical person follow Plan?
- [ ] Is there any "figure out" or "as appropriate"?

If any answer is "No" except the last, you're not ready for non-reasoning.

## Contrast: Reasoning-First Design

**For Claude 3, o1:**

Tier 1 is acceptable — model can infer.
Implicit rules work — model understands context.
Examples are optional — model generalizes.

**For Haiku, mini-models:**

Only Tier 3 is reliable.
All rules explicit.
Examples critical.

## Key Takeaway

**Non-reasoning models need:**
1. Explicit rules (not inferred)
2. Narrow, procedural steps
3. Schema-based output
4. Minimal ambiguity

**Use [[01-System-Prompt-Design-Framework]] as designed**, but make everything **more explicit** than you would for reasoning models.

## Relates To

- [[06-Tiered-Complexity-Model]] — Tier 3 recommended
- [[04-Execution-Plan-Component]] — More granular steps needed
- [[05-Rule-Blocks-Component]] — More detailed rules needed
- [[11-Brief-Writing-Agent]] — Example adapted for Haiku

# Learnings & Insights

## Key Findings from Research

Empirical insights and best practices discovered through building agents with [[01-System-Prompt-Design-Framework]].

---

## Insight 1: Orthogonality Prevents Maintenance Hell

**Finding:** Prompts without [[02-Orthogonality-Principle]] have exponential maintenance cost.

**Evidence:** Brief-Writing Agent (Tier 3):
- With orthogonal structure: 1 place to change rule blocks
- Without: Same rules duplicated in Task, Plan, Rule Blocks

**Cost of Duplication:**
- 2 copies → 2x review burden
- 3 copies → 3x update burden
- But costs don't add; they multiply (inconsistency risk)

**Lesson:** Invest in orthogonal structure upfront. It pays back immediately when rules change.

---

## Insight 2: Non-Reasoning Models Need Tier 3, Always

**Finding:** [[15-Non-Reasoning-Model-Design]] is non-negotiable for models like Claude Haiku.

**Evidence:** Brief-Writing Agent on Haiku:
- Tier 1 (Task only): 40% hallucination rate (made up citations, formatting)
- Tier 2 (Task + Plan): 15% error rate (missing validation steps)
- Tier 3 (Task + Plan + Rules): <2% error rate

**Lesson:** Don't shortcut Tier structure for "smaller" models. They need MORE structure, not less.

---

## Insight 3: Gap Highlighting Prevents Confusion

**Finding:** [[17-Markup-and-Highlighting]] with explicit gap markers dramatically improves usability.

**Evidence:** Brief-Writing Agent:
- Without gaps: Users don't notice missing data (output looks complete)
- With gap marks: Missing data is impossible to ignore

**Lesson:** Explicit gap markers (`<mark data-type="gap">TBD</mark>`) are better UX than implicit "missing data".

---

## Insight 4: First Step Must Be Guardrails

**Finding:** [[14-Guardrail-System]] should be **first** validation, not last.

**Evidence:**
- Guardrail at end: Agent wastes effort processing out-of-scope requests
- Guardrail at start: Reject immediately, no wasted effort

**Cost:** Querying databases, processing data, formatting output for a request you'll reject anyway.

**Lesson:** Put guardrails in [[04-Execution-Plan-Component]] Step 1, always.

---

## Insight 5: Schema-First Output Improves Consistency

**Finding:** Defining output schema before coding the agent ensures consistent structure.

**Evidence:**
- With schema-first: 98% structural consistency
- Without schema-first: 60% consistency (agent invents variations)

**Lesson:** Before [[04-Execution-Plan-Component]], define [[05-Rule-Blocks-Component]] schema.

---

## Insight 6: Examples Belong Only in Rule Blocks

**Finding:** Examples in Task or Plan cause model hallucination.

**Evidence:** Sales Agent:
- Example in Task: Agent invents variations beyond example
- Example in Rule Block only: Agent follows pattern exactly

**Why:** Models generalize from examples (creative). Rule Blocks are prescriptive (deterministic).

**Lesson:** Never put examples in Task or Plan. Rule Blocks only, and kept minimal.

---

## Insight 7: Citation Mapping Prevents Category Chaos

**Finding:** [[13-Citation-System]] with explicit Context Source Mapping prevents citation category drift.

**Evidence:** Brief-Writing Agent:
- Without mapping: Same source cited as 3 different categories
- With mapping: Consistent category assignment

**Lesson:** Create context mapping rules early. Make categorization explicit.

---

## Insight 8: Validation Steps Are Not Optional

**Finding:** [[08-Validation-Discipline]] validation steps catch 90% of errors before user sees them.

**Evidence:** Quoting Agent:
- No validation: 15% incorrect quotes reach user
- With validation: <0.5% incorrect quotes

**Lesson:** Budget 30-40% of Plan steps for validation. It's worth it.

---

## Insight 9: Tier Selection Matters More Than Model Power

**Finding:** A Tier 3 prompt on Haiku outperforms a Tier 1 prompt on Claude 3.

**Evidence:**
- Tier 1 on Claude 3: Hallucination, inconsistency, user frustration
- Tier 3 on Haiku: Reliable, consistent, predictable

**Why:** Structure > Raw capability. Well-defined constraints beat raw intelligence.

**Lesson:** Choose tier based on requirements, not model power.

---

## Insight 10: Semantic Markup Enables Frontend Flexibility

**Finding:** [[17-Markup-and-Highlighting]] with semantic markup (not hardcoded styles) enables UI changes without prompt changes.

**Evidence:**
- Hardcoded styles: UI team can't change colors without rewriting prompts
- Semantic markup: UI team changes CSS, prompt unchanged

**Lesson:** Keep prompt semantic. Styling is frontend's job.

---

## Insight 11: Rejection > Fallback

**Finding:** [[14-Guardrail-System]] should always reject out-of-scope, never fallback.

**Evidence:** Brief-Writing Agent:
- With fallback ("I can try..."):Users get mediocre output outside scope
- With hard rejection: Users know to use different tool

**Lesson:** Be firm. No exceptions. No "best effort" on out-of-scope requests.

---

## Insight 12: Plan Steps Should Be Atomic

**Finding:** Granular, single-action steps in [[04-Execution-Plan-Component]] improve reliability.

**Evidence:**
- Vague steps ("process data"): Model invents sub-steps, often wrong
- Atomic steps ("extract fields", "validate types", "assemble JSON"): Model executes each precisely

**Lesson:** Break steps down until each step is mechanical (could be a function).

---

## Insight 13: Context Source Mapping Prevents Citation Ambiguity

**Finding:** Explicit mapping (header → category) prevents citation inconsistency.

**Evidence:** Brief-Writing Agent:
- Without mapping: Same source sometimes cited as "Creative", sometimes "Workflow"
- With mapping: Consistent categorization

**Lesson:** Create mapping rules upfront. Make them explicit. Enforce during validation.

---

## Insights About Anti-Patterns

### Anti-Pattern: "Tone Rules in Task"

**Problem:** Task shouldn't define tone (HOW agent communicates).

**Example:**
```
❌ Task: "Use a friendly, conversational tone"
```

**Fix:**
```
✅ Rule Block: "Tone Rules: Friendly, conversational, never technical jargon"
```

**Why:** Tone is implementation detail, not acceptance criteria.

---

### Anti-Pattern: "Examples in Plan"

**Problem:** Examples in Plan cause hallucination.

**Example:**
```
❌ Plan: "Generate response like: 'Hi customer, your issue is...' "
```

**Fix:**
```
✅ Rule Block: "Response Format: [Greeting] [Issue summary] [Solution]"
Plan: "Generate response per Response Format Rules"
```

---

### Anti-Pattern: "Validation at End"

**Problem:** Wasted effort if output is invalid.

**Example:**
```
❌ Plan: [steps 1-5] → [step 6] validate

→ If invalid, we wasted 5 steps
```

**Fix:**
```
✅ Plan: [step 0] guardrail → [steps 1-3] generate → [step 4] validate → [step 5] respond
```

---

## Best Practices Checklist

- [ ] Task defines WHAT, not HOW
- [ ] Plan defines HOW, not WHAT or syntax
- [ ] Rule Blocks define syntax and rules only
- [ ] No duplication across components
- [ ] Validation steps are atomic and early
- [ ] Guardrails are Step 1
- [ ] Examples only in Rule Blocks
- [ ] Schema defined before implementation
- [ ] Output uses semantic markup only
- [ ] Non-reasoning models use Tier 3

## Anti-Patterns Checklist

- [ ] Task doesn't contain "first", "then", "next"
- [ ] Plan doesn't contain rule definitions
- [ ] Rule Blocks don't contain procedural steps
- [ ] No rule content is duplicated
- [ ] No inline styling (semantic markup only)
- [ ] Guardrails are first step
- [ ] No examples in Task or Plan
- [ ] All validation is explicit (not implicit)

## Relates To

- [[01-System-Prompt-Design-Framework]] — Framework these insights follow
- [[06-Tiered-Complexity-Model]] — Tier selection guidance
- [[09-Anti-Patterns]] — Patterns to avoid
- [[15-Non-Reasoning-Model-Design]] — Model-specific insights

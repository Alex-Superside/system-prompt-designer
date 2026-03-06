# Key Takeaways

## The Big Picture

System prompt design is fundamentally about **scalability through structure**.

The [[01-System-Prompt-Design-Framework]] trades upfront design cost for long-term maintainability.

---

## Core Principles (TL;DR)

### 1. Orthogonality Scales

**Principle:** Separate WHAT (Task), HOW (Plan), and DETAILS (Rules).

**Benefit:** Change one component without breaking others.

**Cost:** More upfront structure; less flexibility.

**Truth:** Worth it for anything beyond exploratory use.

---

### 2. Tier Selection Matters

**Tier 1 (Task only):** Creative exploration. Fast. Unpredictable.

**Tier 2 (Task + Plan):** Light structure. Balanced.

**Tier 3 (Task + Plan + Rules):** Production. Deterministic. Maintainable.

**Truth:** Choose tier based on risk, not model power. Non-reasoning models need Tier 3.

---

### 3. Validation Must Be Explicit

**Principle:** What gets validated, by whom, and when.

**Responsibility:** [[08-Validation-Discipline]] (Task owns criteria, Plan owns enforcement).

**Truth:** Implicit validation fails silently. Explicit validation catches errors early.

---

### 4. Rules Are Single Source of Truth

**Principle:** Define each rule once. Reference it everywhere else.

**Violation:** Duplication (same rule in Task, Plan, Rules).

**Truth:** Duplication is technical debt. Repay it immediately.

---

### 5. Non-Reasoning Needs Explicitness

**Principle:** Smaller/faster models need more explicit guidance.

**Example:** Haiku needs Tier 3; reasoning models can work with Tier 1.

**Truth:** Structure is more important than raw capability.

---

## The Orthogonality Checklist

Before shipping any prompt, answer these:

### Task
- [ ] Does it define acceptance criteria (MUST/NEVER)?
- [ ] Does it specify output format?
- [ ] Does it reference (not define) Rule Blocks by name?
- [ ] Does it contain NO steps or procedural language?

### Execution Plan
- [ ] Are steps ordered and atomic?
- [ ] Does it apply Rule Blocks by reference?
- [ ] Does it contain validation logic?
- [ ] Does it contain NO rule definitions or formatting?

### Rule Blocks
- [ ] Do they define syntax and formatting rules?
- [ ] Do they contain examples (if any)?
- [ ] Are they referenced (not duplicated) in Task/Plan?
- [ ] Are names stable (not frequently changed)?

### Across Components
- [ ] Is any content duplicated?
- [ ] Is ownership clear (who does what)?
- [ ] Can you follow [[07-Placement-Router]] for every line?

If all answers are "Yes", you're orthogonal.

---

## Common Mistakes (Don't Do These)

### ❌ Mistake 1: Tone Rules in Task

```
Task: "Use a friendly, consultative tone"

→ This is HOW to communicate, not WHAT to output
→ Move to Rule Blocks
```

### ❌ Mistake 2: Examples in Plan

```
Plan: "Generate response like: 'Hi customer...'"

→ Plan shouldn't specify examples
→ Move to Rule Blocks, or remove entirely
```

### ❌ Mistake 3: Guardrails Not First

```
Plan: [steps 1-5] then [check scope]

→ Wasted effort if out-of-scope
→ Move check to Step 1
```

### ❌ Mistake 4: Implicit Validation

```
Task: "Output MUST be valid JSON"
Plan: [no validation step]

→ How is validity checked? By whom?
→ Add explicit validation step to Plan
```

### ❌ Mistake 5: Hardcoded Styling

```
<mark style="background-color: yellow;">text</mark>

→ Mixes prompt and UI concerns
→ Use semantic markup: <mark class="highlight" data-type="citation">text</mark>
```

---

## The Minimum Viable Prompt

**For Tier 1 (Task Only):**
```
Objective: [1 sentence]
Acceptance Criteria: [MUST/NEVER statements]
Output: [format description]
```

**For Tier 2 (Task + Plan):**
```
Task: [WHAT]
Plan: [steps]
```

**For Tier 3 (Task + Plan + Rules):**
```
Task: [WHAT]
Execution Plan: [steps] (with validation)
Rule Blocks:
  - [Name]: [syntax/rules]
  - [Name]: [syntax/rules]
```

Start small. Add structure as complexity grows.

---

## When to Use This Framework

### Use [[01-System-Prompt-Design-Framework]]

✅ Multi-agent systems
✅ Production agents
✅ Compliance-critical tasks
✅ Non-reasoning models
✅ Frequently-updated rules
✅ Team-maintained prompts

### Skip (Use Tier 1 Instead)

❌ One-off exploration
❌ Creative ideation
❌ Personal/experimental use
❌ Low-risk outputs

---

## The Real Cost-Benefit

### Upfront Cost

- Time to design Task/Plan/Rules
- Discipline to avoid shortcuts
- Learning curve for framework

### Long-Term Benefit

| Scenario | Without Framework | With Framework |
|---|---|---|
| Change a rule | Edit 3 places, review 3 times | Edit 1 place, review 1 time |
| Onboard new contributor | "Read the prompt" (confusing) | "Read Task, then Plan, then Rules" (clear path) |
| Debug error | Search entire prompt | Check validation step in Plan |
| Add new agent | Copy-paste existing | Reuse Rule Blocks, new Task/Plan |
| Scale to 10 agents | Maintenance nightmare | Smooth (Rules are shared) |

**Verdict:** Pays back after 2-3 agents or 2-3 rule changes.

---

## Relationship to LLM Capability

### Myth: Better Models Need Less Structure

**Truth:** The opposite.

**Why?**
- Better models can infer intent from poor prompts
- But you're using their capability to guess
- That's wasteful (and unreliable at scale)

### Better Models + Great Prompts

- Model capability amplifies structure
- Structure prevents hallucination
- Result: Predictable, scalable, maintainable

### Smaller Models Need Structure

- Can't infer from hints
- Need explicit rules
- Tier 3 is non-negotiable

**Bottom line:** Great prompts matter more than great models.

---

## Evolution Path

### Phase 1: Discover (Tier 1)

Explore what your agent needs to do.
- Task only
- Iterate rapidly
- Document learnings

### Phase 2: Structure (Tier 2)

Add light structure as needs clarify.
- Task + minimal Plan
- Identify core rules
- Separate concerns

### Phase 3: Optimize (Tier 3)

Formalize rules, enable scaling.
- Task + Plan + Rule Blocks
- Full orthogonality
- Ready for production

**Don't skip Phase 1.** You can't design Tier 3 without understanding requirements.

---

## Final Wisdom

### On Orthogonality

> "Good system prompts are boring, predictable, and easy to change."

If your prompt is exciting to read, it's probably poorly designed.

### On Maintainability

> "If you see duplication, the architecture is leaking."

Act immediately. Don't let debt accumulate.

### On Modeling Capability vs. Structure

> "Structure is more important than raw capability."

A Haiku-3.5 with Tier 3 structure beats Claude 3 with a handwavy prompt.

### On Scaling

> "You can't scale without structure."

Tier 1 prompts stop scaling at 2-3 agents. Tier 3 scales to hundreds.

---

## Next Steps

1. **Start small:** Pick one agent. Use [[01-System-Prompt-Design-Framework]].
2. **Follow the pattern:** Use [[18-Design-Patterns-by-Agent]] for your agent type.
3. **Validate orthogonality:** Use [[07-Placement-Router]] on every line.
4. **Test thoroughly:** Use [[08-Validation-Discipline]] checklist.
5. **Document learnings:** Add to [[19-Learnings-and-Insights]].

---

## Key Document References

| Concept | Document |
|---|---|
| Overall framework | [[01-System-Prompt-Design-Framework]] |
| Design tool | [[07-Placement-Router]] |
| Real-world example | [[11-Brief-Writing-Agent]] |
| Agent patterns | [[18-Design-Patterns-by-Agent]] |
| Avoiding mistakes | [[09-Anti-Patterns]] |
| Non-reasoning models | [[15-Non-Reasoning-Model-Design]] |
| Best practices | [[19-Learnings-and-Insights]] |

---

## TL;DR

**System prompt design is an engineering discipline, not an art form.**

Use [[01-System-Prompt-Design-Framework]] for production systems.

- Separate WHAT, HOW, and DETAILS
- Choose tier based on risk, not model power
- Validate everything explicitly
- Never duplicate rules
- Keep prompts boring

The reward: Maintainable, scalable, reliable agents.

---

## Relates To

- [[00-Index]] — Start here to explore
- [[01-System-Prompt-Design-Framework]] — Foundation
- [[06-Tiered-Complexity-Model]] — Practical guidance
- [[19-Learnings-and-Insights]] — Empirical findings

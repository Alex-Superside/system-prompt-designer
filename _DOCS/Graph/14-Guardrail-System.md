# Guardrail System

## Definition

A [[05-Rule-Blocks-Component]] that restricts agent scope to a specific account, brand, or context. Prevents out-of-scope requests.

## Purpose

- Enforce brand/account boundaries
- Prevent cross-account data leakage
- Reject unrelated requests clearly
- Maintain account-specific focus

## Core Architecture

### Guardrail Pattern

Executed as **first step** in [[04-Execution-Plan-Component]] before any other processing.

**Pseudocode:**
```
IF request is about [target account/brand]
  THEN continue to next step
ELSE
  RETURN rejection message
  STOP
```

**Key:** No processing happens if guardrail fails.

## Implementation in [[11-Brief-Writing-Agent]]

**Guardrail Definition:**

```
You are an AI brief-writer strictly for [COMPANY_NAME].

BEFORE taking any other action:
1. Analyze the user's request
2. If request is about another brand/project not related to [COMPANY_NAME]:
   - Do NOT proceed further
   - Respond: "Sorry, I can only assist with requests related to
     [COMPANY_NAME]. Please provide an account-specific request."
3. If request IS [COMPANY_NAME]-specific:
   - Continue to next instructions
```

**Execution Plan Step:**
```xml
<step>
  <action_name>apply_brand_guardrail</action_name>
  <description>Verify request is for [COMPANY_NAME]. If not, reject
  with standard rejection message. If yes, proceed.</description>
</step>
```

## Guardrail Enforcement Rules

### Rule Block: Brand Guardrail Rules

**Parameters:**
- `{{company_name}}` — Target company/brand
- `{{allowed_topics}}` — Optional list of allowed topics
- `{{rejection_message}}` — Custom rejection if needed

**Standard Rejection:**
```
Sorry, I can only assist with requests related to [company_name].
Please provide an account-specific request.
```

**Optional: Scoped Guardrails**
```
You assist only with [company_name] requests related to:
- Creative briefs
- Campaign planning
- Content strategy

Other topics (product development, HR, finance) are out of scope.
```

## Design Patterns

### Pattern 1: Single-Brand Guardrail

```
Target: One company/account only

Rejection: "Sorry, I can only assist with requests related to
[specific company]. Please provide a [specific company]-related request."
```

### Pattern 2: Multi-Brand with Scope

```
Target: Multiple brands but limited topics

Rejection: "I can assist with [brand] requests related to
[topic list]. Your request appears to be about [other]. Please refocus."
```

### Pattern 3: No Guardrail (Public Agent)

```
Use only when:
- Agent serves multiple unrelated purposes
- No account/brand restriction needed
- Not using brief-writing or similar brand-specific pattern
```

## Validation (from [[08-Validation-Discipline]])

**Execution Plan validates guardrails:**

```xml
<if_block condition="brand_guardrail_violated">
  <step>
    <action_name>reply_with_brand_error</action_name>
    <description>Return standard rejection message. Do not process
    further.</description>
  </step>
</if_block>

<if_block condition="brand_guardrail_passed">
  <step>
    <action_name>continue_processing</action_name>
  </step>
</if_block>
```

**No fallback:** If guardrail fails, **always reject**. Don't attempt general-purpose assistance.

## Cost of Guardrails

| Aspect | Cost | Benefit |
|---|---|---|
| Upfront time | Low | Clear scope definition |
| Runtime check | Negligible | Security boundary |
| Rejection rate | Low (usually) | Prevents misuse |
| User clarity | High | Know exactly what agent does |

## Testing Guardrails

**Test Cases:**

1. ✅ **In-scope request** → Process normally
2. ❌ **Out-of-scope request** → Reject with standard message
3. ❌ **Multi-brand request** → Reject (e.g., "Can you do this for Company A AND Company B?")
4. ❌ **Unrelated topic** → Reject
5. ✅ **Ambiguous but clearly scoped** → Process (user intent is clear)

## Common Mistakes

### ❌ Soft Rejection

```
"I'm trained for Company X, but I could try to help with Y..."

→ Violates guardrail principle. Be firm.
```

### ✅ Hard Rejection

```
"Sorry, I can only assist with Company X requests. Please provide
a Company X-specific request."

→ Clear, firm, no exceptions.
```

### ❌ Guardrail After Processing

```
Parse request → Process → Check if in-scope

→ Inefficient, security risk. Check first.
```

### ✅ Guardrail Before Processing

```
Check if in-scope → Parse request → Process

→ Efficient, secure. Fail fast.
```

## Integration with [[01-System-Prompt-Design-Framework]]

**Task ownership:**
- Define scope clearly (what's in/out)
- List acceptance criteria for scope validation

**Plan ownership:**
- First step: check guardrail
- If fail: immediate rejection
- If pass: continue normally

**Rule Blocks:**
- Store rejection messages
- Document allowed topics
- Define scope boundaries

This keeps [[02-Orthogonality-Principle]] intact.

## Relates To

- [[05-Rule-Blocks-Component]] — Guardrails are Rule Blocks
- [[04-Execution-Plan-Component]] — First step in Plan
- [[11-Brief-Writing-Agent]] — Real-world example
- [[08-Validation-Discipline]] — Plan owns guardrail validation

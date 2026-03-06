# Validation Discipline

## Definition

Clear ownership of validation responsibilities across [[03-Task-Component]], [[04-Execution-Plan-Component]], and [[05-Rule-Blocks-Component]].

## Ownership Model

### Task Owns

**Acceptance Criteria**
- MUST / NEVER statements
- Output format guarantees
- High-level constraints
- Success/failure conditions

**Example:**
- MUST follow Product Rules
- MUST output JSON only
- MUST never infer unknown values

### Execution Plan Owns

**Preflight Checks**
- Input validation before processing
- Required field presence checks
- Data type validation

**Schema Validation**
- Structural conformance
- Required fields presence
- Type checking
- Array/object integrity

**Numbering and ID Integrity**
- Sequential citation numbering
- Unique ID generation
- Reference integrity

**Conditional Responses**
- if/then logic based on validation results
- Error responses
- Partial data handling (TBD/GAP placeholders)

**Example Steps:**
- Validate user input has required fields
- Check JSON structure matches schema
- Verify all citations are numbered
- Return error if validation fails

### Rule Blocks Define How

Rule Blocks don't **do** validation—they **define** the rules validation enforces.

**Example Rule Blocks:**
- JSON Schema Rules (structure definition)
- Pricing Rules (valid price ranges)
- Citation Formatting Rules (allowed markup)

The Plan applies these rules through validation steps.

## Anti-Patterns

### ❌ Dual Ownership

Task and Plan both defining scope:
```
Task: "Output must be valid JSON"
Plan: "Generate JSON strictly per JSON Schema"
→ Duplication
```

**Fix:**
```
Task: "Output must be valid JSON per Schema Rules"
Plan: "Assemble JSON strictly per JSON Schema Rules; validate structure"
Rule Block: "JSON Schema Rules: {...}"
```

### ❌ No Validation

Task expects output, Plan never validates:
```
Task: "MUST insert TBD for missing values"
Plan: [no validation check for TBD placement]
→ Acceptance criteria can't be verified
```

**Fix:**
Add Plan step: "validate_tbd_placement: Check all TBD values match TBD Rules"

### ❌ Validation in Rule Blocks

Rule Blocks describing procedures:
```
Rule: "When validating JSON, first parse, then check types..."
→ This is procedural, not definitional
```

**Fix:**
```
Rule: "JSON Schema: {...}"
Plan: "Step: validate_json per JSON Schema Rules"
```

## Validation Chain

```
Task (Defines What's Valid)
  ↓
Execution Plan (Validates + Acts)
  ├─ Preflight checks
  ├─ Parse/map input
  ├─ Apply Rule Blocks
  ├─ Validate output against rules
  └─ Return valid or error
  ↑
Rule Blocks (Define Rules)
```

## Real-World Example: Brief-Writing Agent

**Task owns:**
- MUST include citations
- MUST mark gaps with <mark class="highlight" data-type="gap">

**Plan owns:**
- Validate citations are sequentially numbered
- Check all required sections present
- Validate gap markers are properly formed

**Rule Blocks own:**
- Citation Formatting Rules (markup syntax)
- Gap Highlighting Rules (HTML structure)
- Context Source Mapping Rules (how to cite)

## Testing Validation Discipline

Ask these questions:

1. **Can [[03-Task-Component]] acceptance criteria be verified?**
   - If no → [[04-Execution-Plan-Component]] needs validation step

2. **Are all validations mentioned in [[04-Execution-Plan-Component]]?**
   - If no → Add validation steps

3. **Are any validation procedures in [[05-Rule-Blocks-Component]]?**
   - If yes → Move to Plan

4. **Do [[05-Rule-Blocks-Component]] define what's valid, not how to validate?**
   - If no → Rewrite as rule definition, not procedure

## Relates To

- [[01-System-Prompt-Design-Framework]] — Overall architecture
- [[04-Execution-Plan-Component]] — Where validation happens
- [[09-Anti-Patterns]] — What breaks validation

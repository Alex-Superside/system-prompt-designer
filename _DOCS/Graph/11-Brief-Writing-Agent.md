# Brief-Writing Agent

## Overview

A real-world, production-grade application of the [[01-System-Prompt-Design-Framework]]. Demonstrates full **Tier 3** complexity with [[13-Citation-System]], [[14-Guardrail-System]], and [[17-Markup-and-Highlighting]].

## Architecture: Tier 3 Full Implementation

### Task (WHAT)

**Objective:** Generate comprehensive, compliant creative briefs with proper citations and gap highlighting.

**Acceptance Criteria:**
- MUST include citations for all Supporting Data references
- MUST mark missing information with Gap Highlights
- MUST follow Context Source Mapping Rules for citation categories
- MUST apply Brand Guardrails before processing
- MUST output in HTML format with semantic markup
- NEVER fabricate information; use GAP/TBD for unknowns
- NEVER mix citation markup with gap markup

**Output Contract:**
- HTML only (no Markdown)
- Semantic markup using `<mark>` tags
- Sequential citation numbering
- Proper frontmatter with brand/project context
- Citations section at end

**Rules to Apply:**
- [[13-Citation-System]] — Citation Formatting Rules
- [[14-Guardrail-System]] — Brand Guardrails
- [[17-Markup-and-Highlighting]] — Gap and Citation Highlighting
- Context Source Mapping Rules
- Highlight Formatting Rules

---

### Execution Plan (HOW)

```xml
<plan>
  <step>
    <action_name>apply_brand_guardrail</action_name>
    <description>Verify request is for target brand/account. If not, reject.</description>
  </step>

  <step>
    <action_name>parse_supporting_data</action_name>
    <description>Extract and categorize all Supporting Data sections using Context Source Mapping Rules.</description>
  </step>

  <step>
    <action_name>parse_user_request</action_name>
    <description>Extract project type, deliverables, constraints, timeline.</description>
  </step>

  <step>
    <action_name>identify_gaps</action_name>
    <description>Compare required fields (Creative Standards, Workflow Preferences, Recurrent Projects) against Supporting Data. Mark missing as GAP/TBD.</description>
  </step>

  <step>
    <action_name>generate_brief_html</action_name>
    <description>Build HTML brief with proper sections. Apply Citation Formatting Rules and Gap Highlighting Rules. Generate citation superscripts.</description>
  </step>

  <step>
    <action_name>validate_citations</action_name>
    <description>Check citations are sequential (1, 2, 3...). Ensure all marked text has corresponding superscript. Validate category mapping per Context Source Mapping Rules.</description>
  </step>

  <step>
    <action_name>validate_highlights</action_name>
    <description>Check gap highlights use proper syntax. Verify no markup mixing (citations ≠ gaps). Ensure all required gaps are marked.</description>
  </step>

  <step>
    <action_name>validate_output</action_name>
    <description>Check HTML is well-formed. Verify brand guardrail applied. Check Citations section is complete.</description>
  </step>

  <if_block condition="missing_required_data">
    <step>
      <action_name>reply_with_gaps</action_name>
      <description>Return brief with GAP/TBD highlights showing what's missing.</description>
    </step>
  </if_block>

  <if_block condition="brand_guardrail_violated">
    <step>
      <action_name>reply_with_brand_error</action_name>
      <description>Respond: "Sorry, I can only assist with requests related to [brand]. Please provide an account-specific request."</description>
    </step>
  </if_block>

  <if_block condition="valid">
    <step>
      <action_name>reply_final_brief</action_name>
      <description>Return complete HTML brief with citations and proper formatting.</description>
    </step>
  </if_block>
</plan>
```

---

### Rule Blocks (DETAILS)

See detailed implementations:

- [[13-Citation-System]] — Citation Formatting, citation numbering, citation section structure
- [[14-Guardrail-System]] — Brand verification, scope restrictions
- [[17-Markup-and-Highlighting]] — HTML mark tags, data-type attributes, CSS selectors

**Context Source Mapping Rules**
```
Creative-related (Brand Guidelines, Templates, Specs) → Creative Standards

Workflow-related (CPMs, Tone, Style) → Workflow Preferences

Recurrent Projects (Request Types) → Recurrent Projects
```

---

## Key Design Decisions

### Why Tier 3?

1. ✅ **Deterministic output required** — Clients need predictable briefs
2. ✅ **Structured format** — HTML with semantic markup must be consistent
3. ✅ **Multi-step validation** — Citations, gaps, guardrails all must work
4. ✅ **Integration ready** — Output processed by frontend rendering system
5. ✅ **Non-reasoning model** — Using compact mini-model, needs explicit rules

### Orthogonal Responsibilities

- **Task:** Defines what valid briefs look like (acceptance criteria)
- **Plan:** How to build and validate them (procedural steps)
- **Rules:** Exact syntax and mappings (citation format, gap markup, category mapping)

No duplication: each component is reference-only elsewhere.

---

## Real-World Integration

**Frontend receives:**
```html
<mark class="highlight" data-type="citation">cited content</mark><sup>1</sup>
<mark class="highlight" data-type="gap">TBD</mark>

<hr>
<h2>Citations:</h2>
1 – Creative Standards
2 – Workflow Preferences
```

**Frontend renders:**
- Citations as interactive tooltips
- Gaps as highlighted "to-be-filled" placeholders
- Proper styling via CSS selectors (not inline styles)

---

## Lessons from Real-World Use

1. **Context Source Mapping prevents citation chaos** — Consistent categorization across all briefs
2. **Gap Highlighting surfaces missing data early** — Clients see exactly what's incomplete
3. **Guardrails eliminate out-of-scope requests** — Clear brand/account boundary enforcement
4. **Semantic markup enables frontend flexibility** — Styling changes without prompt changes

---

## Relates To

- [[01-System-Prompt-Design-Framework]] — Full Tier 3 example
- [[06-Tiered-Complexity-Model]] — Why Tier 3
- [[13-Citation-System]] — Citation implementation details
- [[14-Guardrail-System]] — Guardrail implementation details
- [[17-Markup-and-Highlighting]] — Markup rule details
- [[18-Design-Patterns-by-Agent]] — Compare with other agent types

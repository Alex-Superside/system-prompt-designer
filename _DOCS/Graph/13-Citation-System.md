# Citation System

## Definition

A [[05-Rule-Blocks-Component]] that enables agents to track and cite sources from Supporting Data, ensuring transparency and traceability.

## Purpose

- Provide provenance for every factual statement
- Enable citation of multiple data sources
- Make source attribution explicit and structured
- Support frontend rendering of interactive citations

## Core Components

### 1. Citation Formatting Rules

**Markup Structure**
```html
<mark data-type="citation" data-citation-id="1">
  [Referenced text from Supporting Data]
</mark>
<sup
  data-citation-id="1"
  data-id="contextItem_103"
  data-type="brand_brain"
  data-title="Account DOs and DON'Ts"
  data-reasoning="Derived from Account DOs and DON'Ts section."
>1</sup>
```

**Key Elements:**
- `<mark>` tag wraps cited text
- `data-type="citation"` identifies citation type
- `<sup>` superscript number immediately after
- Metadata attributes on `<sup>` tag

### 2. Context Source Mapping Rules

Maps Supporting Data headers to citation category labels.

**Mapping Table**

| Section Header Keywords | Citation Category |
|---|---|
| Creative DOs & DON'Ts, Brand Guidelines, Templates, Specs | Creative Standards |
| CPMs DOs & DON'Ts, Customer Tone, Writing Style | Workflow Preferences |
| Request Type, Recurrent Projects | Recurrent Projects |

**Why:** Allows consistent citation naming across all documents.

### 3. Citation Numbering Rules

- **Sequential:** 1, 2, 3, 4... (not alphabetical or by source)
- **Document-wide:** Numbering continuous from start to end
- **One superscript per citation instance**
- **Citations section at end** lists all sources

### 4. Citations Section Format

```html
<hr>
<h2>Citations:</h2>
1 – Creative Standards<br>
2 – Workflow Preferences<br>
3 – Recurrent Projects
```

**Rules:**
- Appears after document content
- One line per citation
- Lists only categories actually cited (not unused categories)
- Numerical order

## Implementation in [[11-Brief-Writing-Agent]]

**Execution Plan steps:**
1. parse_supporting_data — Identify source sections
2. Map each section to category using Context Source Mapping Rules
3. generate_brief_html — Mark citations with proper syntax
4. validate_citations — Check sequential numbering and category mapping

**Output Example:**

```html
<p>
We want you to adhere to
<mark data-type="citation">Brand Guidelines</mark><sup>1</sup>
as established in previous projects.
</p>

<ul>
<li><mark data-type="citation">Video format: 1920×1080 MP4</mark><sup>2</sup></li>
</ul>

<hr>
<h2>Citations:</h2>
1 – Creative Standards<br>
2 – Creative Standards
```

## Frontend Rendering

Citations are **styled by frontend**, not prompt:

```css
/* Frontend CSS controls appearance */
mark[data-type="citation"] {
  background-color: #fff3cd; /* Yellow highlight */
}

mark[data-type="citation"]:hover {
  background-color: #ffeaa7; /* Darker on hover */
}

sup[data-citation-id] {
  cursor: pointer; /* Indicate interactivity */
}
```

Agents should only output semantic markup, not styling.

## Common Mistakes

### ❌ Multiple Superscripts for Same Text

```html
<mark>Text</mark><sup>1</sup><sup>2</sup>

→ Violates single-superscript rule
```

### ❌ Large superscript numbers

```html
<mark>Text</mark><sup data-citation-id="103">103</sup>

→ Should renumber sequentially to 1, 2, 3...
```

### ❌ Citation in Citations Section

```html
Citation: <mark>Creative Standards</mark><sup>1</sup>

→ Citations section itself should not be cited
```

### ❌ Missing metadata on superscript

```html
<mark>Text</mark><sup>1</sup>

→ Should include data-id, data-type, data-title, data-reasoning
```

## Testing Citations

**Validation Steps (from [[04-Execution-Plan-Component]]):**

1. All citations sequential? (1, 2, 3... no gaps)
2. Each superscript has metadata attributes?
3. data-citation-id matches between `<mark>` and `<sup>`?
4. Citations section lists all unique categories?
5. Citations section in correct order (1, 2, 3...)?

## Reusability

Citation Rules can be reused in:
- [[11-Brief-Writing-Agent]] — Brief citations
- [[12-Agent-Types#FAQ-Responder]] — FAQ source citations
- Any agent producing cited output

This is why [[02-Orthogonality-Principle]] matters: Rule Blocks are reusable once decoupled from specific agents.

## Relates To

- [[05-Rule-Blocks-Component]] — Citation Rules are a Rule Block
- [[11-Brief-Writing-Agent]] — Primary use case
- [[17-Markup-and-Highlighting]] — Related markup system
- [[08-Validation-Discipline]] — Plan validates citations

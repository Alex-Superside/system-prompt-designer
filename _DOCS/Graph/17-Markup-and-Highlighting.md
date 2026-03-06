# Markup & Highlighting System

## Definition

A [[05-Rule-Blocks-Component]] that uses semantic HTML markup to highlight gaps, citations, and other content without hardcoding visual styling.

## Core Principle

**Markup is semantic, styling is frontend.**

Agents output structural markup with `data-*` attributes; CSS controls appearance.

## HTML Markup Tags

### 1. Mark Tag Structure

```html
<mark class="highlight" data-type="[type]">[content]</mark>
```

**Attributes:**
- `class="highlight"` — Identifies it as a special mark
- `data-type="[type]"` — Semantic type (gap, citation, etc.)
- Content — The highlighted text

### 2. Types

#### Citation Type

```html
<mark class="highlight" data-type="citation">cited text</mark><sup>1</sup>
```

**Used for:**
- Text sourced from Supporting Data
- References to previous guidelines
- Any cited content

**Styling hook:** `mark[data-type="citation"]`

#### Gap Type

```html
<mark class="highlight" data-type="gap">TBD</mark>
```

or

```html
<mark class="highlight" data-type="gap">No data provided</mark>
```

**Used for:**
- Missing information
- Unknown values
- Incomplete specifications

**Styling hook:** `mark[data-type="gap"]`

#### Default Type

```html
<mark class="highlight">unverified information</mark>
```

**Used for:**
- Information needing verification
- Uncertain content
- Assumptions to confirm

**Styling hook:** `mark.highlight`

## CSS Control (Frontend)

Agents never specify styling—CSS is frontend-only:

```css
/* Frontend defines visual appearance */

mark[data-type="citation"] {
  background-color: #fff3cd;  /* Yellow */
  border-left: 3px solid #ffc107;
}

mark[data-type="gap"] {
  background-color: #f8d7da;  /* Red/pink */
  border-left: 3px solid #dc3545;
}

mark.highlight {
  background-color: #d1ecf1;  /* Blue */
  border-left: 3px solid #17a2b8;
}

/* Interactive states */
mark[data-type="gap"]:hover {
  background-color: #f5c6cb;
  cursor: pointer;
}
```

## Implementation Rules

### Rule Block: Highlight Formatting Rules

**General Principles**
1. Always use `<mark>` elements with `class="highlight"` and `data-type` attribute
2. Never use inline `style` attributes or `<span>` tags
3. Never output Markdown `==...==` syntax
4. Highlight markers are semantic, not visual

**Gap Highlighting Examples**
```html
No Deadline: <mark class="highlight" data-type="gap">GAP</mark>

Missing Specs: <mark class="highlight" data-type="gap">Need client details</mark>

Timeline: <mark class="highlight" data-type="gap">TBD</mark>
```

**Citation Highlighting Examples**
```html
We follow <mark class="highlight" data-type="citation">Brand Guidelines</mark><sup>1</sup>

Formats: <mark class="highlight" data-type="citation">1920×1080 MP4</mark><sup>2</sup>
```

**Default Highlight Examples**
```html
Specs needed: <mark class="highlight">Need to confirm with client</mark>

Uncertain content: <mark class="highlight">Estimated budget</mark>
```

## Behavioral Notes

- **Visibility:** Highlights are subtle by default (depend on CSS)
- **Interactivity:** May become interactive on hover (frontend decides)
- **Styling:** Frontend controls all colors, borders, animations
- **No hardcoding:** System prompt should never define CSS

## Integration with [[11-Brief-Writing-Agent]]

**Execution Plan generates:**
```html
<p>Creative direction – <mark class="highlight" data-type="gap">TBD</mark></p>
```

**Frontend CSS applies:**
```css
mark[data-type="gap"] { background: #f8d7da; }
```

**User sees:** Red/pink highlighted "TBD"

**Benefit:** If UI team wants to change color, they change CSS, not the agent.

## Real-World Rendering

**Agent output:**
```html
<p>We need to follow <mark class="highlight" data-type="citation">Brand Guidelines</mark><sup>1</sup> and establish <mark class="highlight" data-type="gap">timeline TBD</mark>.</p>
```

**Rendered to user:**
- "Brand Guidelines" appears with yellow highlight + superscript 1
- "timeline TBD" appears with red highlight
- Styling applied by frontend CSS, not hardcoded

## Common Mistakes

### ❌ Inline Styles

```html
<mark style="background-color: yellow;">text</mark>

→ Violates separation of concerns
→ Hard to change styling globally
```

### ✅ Semantic Markup

```html
<mark class="highlight" data-type="citation">text</mark>

→ Frontend controls styling
→ Easy to change globally
```

### ❌ Multiple Data Types

```html
<mark class="highlight" data-type="gap citation">text</mark>

→ Ambiguous. Use one type per mark.
```

### ✅ One Type Per Mark

```html
<mark class="highlight" data-type="gap">TBD</mark>
```

### ❌ Markdown Syntax

```html
We need ==more information==

→ Wrong format. Use <mark> tags.
```

### ✅ HTML Markup

```html
We need <mark class="highlight" data-type="gap">more information</mark>
```

## Accessibility Considerations

**Good practices:**
- Semantic `data-type` attributes enable screen readers
- Color is not the only indicator (add text like "TBD", "CITATION")
- Markup conveys meaning independent of styling

**Example:**
```html
<mark class="highlight" data-type="gap">No timeline specified</mark>

→ Even without highlight color, semantic meaning is clear
```

## Testing Markup

**Validation Steps (from [[04-Execution-Plan-Component]]):**

1. [ ] All marks use `class="highlight"`?
2. [ ] All marks have `data-type` attribute?
3. [ ] No inline `style` attributes?
4. [ ] No Markdown `==...==` syntax?
5. [ ] Gap and citation marks don't overlap?
6. [ ] Content is clear without styling?

## Relates To

- [[05-Rule-Blocks-Component]] — Markup rules are Rule Blocks
- [[13-Citation-System]] — Citation-specific markup
- [[11-Brief-Writing-Agent]] — Real-world application
- [[08-Validation-Discipline]] — Plan validates markup syntax

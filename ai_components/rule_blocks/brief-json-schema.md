## Brief JSON Schema Rules

- The agent MUST return a single top-level JSON object, not an array.
- The object MUST include, at minimum, the keys `title`, `summary`, and `sections`.
- `sections` MUST be an array of objects, each with `heading` and `content` string fields.
- No additional free-form text is allowed outside the JSON block.


# Prompt Design Framework: The Engineering Lifecycle

This framework provides a systematic approach to designing, implementing, and maintaining high-performance system prompts. It is grounded in the principles of structural orthogonality, tiered complexity, and linguistic precision.

## Core Lifecycle Phases

1. **[[00-Linguistic-Foundations]]**: Understanding the gap between human intent and LLM token perception.
2. **[[01-Discovery-and-Tiering]]**: Defining the mission and selecting the appropriate structural complexity.
3. **[[02-Structural-Orthogonality]]**: Architecting the prompt into WHAT (Task), HOW (Plan), and DETAILS (Rules).
4. **[[03-Hardening-and-Validation]]**: Implementing deterministic guardrails and explicit verification steps.
5. **[[04-DSL-and-Token-Optimization]]**: Using Domain-Specific Languages to maximize semantic density and cache efficiency.
6. **[[05-Anti-Patterns-and-Refactoring]]**: Identifying and fixing "leaky" architectures and technical debt.

## Why This Framework?

- **Maintainability**: Update a single rule block without refactoring the entire prompt.
- **Scalability**: Share rule blocks across multiple agents in a system.
- **Reliability**: Reduce hallucinations by replacing "inference" with "instruction."
- **Efficiency**: Optimize for token count and KV-caching without losing nuance.

---
*“Good system prompts are boring, predictable, and easy to change.”*

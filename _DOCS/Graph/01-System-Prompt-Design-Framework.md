# System Prompt Design Framework

## Overview

The foundational architecture for designing system prompts using **non-overlapping responsibilities**. This framework ensures prompts remain maintainable, scalable, and predictable.

## Components

The framework consists of three orthogonal components:

1. [[03-Task-Component]] — WHAT the agent must achieve
2. [[04-Execution-Plan-Component]] — HOW the agent should proceed
3. [[05-Rule-Blocks-Component]] — DETAILS: syntax and logic

## Core Principle

[[02-Orthogonality-Principle]] ensures each component is:
- Independent
- Reference-only (no duplication)
- Single-purpose

## Application Model

[[06-Tiered-Complexity-Model]] — Choose the simplest tier that satisfies requirements:
- Tier 1: Task only
- Tier 2: Task + Minimal Plan
- Tier 3: Task + Plan + Rule Blocks

## Validation

[[07-Placement-Router]] provides a decision filter to determine where each instruction belongs.

[[08-Validation-Discipline]] defines ownership and enforcement of constraints.

## Real-World Application

[[11-Brief-Writing-Agent]] demonstrates full Tier 3 implementation with [[13-Citation-System]] and [[14-Guardrail-System]].

[[12-Agent-Types]] shows how the framework applies to Sales, Quoting, Python agents, and others.

## Common Failures

[[09-Anti-Patterns]] lists duplication, mixed intent, and other violations.

[[10-Orthogonality-Violations]] explains how these break the architecture.

## Key Insight

> "Good system prompts are boring, predictable, and easy to change."

Orthogonality is a scalability pattern, not a dogma. Use the simplest structure that satisfies requirements.

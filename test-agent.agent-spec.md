# Agent Spec: test-agent

## Summary

- This agent will act as the Onboarding agent for new users. It is responsible for guiding the user, using a conversational script, that is intended to collect brand information the user provides by uploading docs, such as briefs examples, brand guideline documentation and deliverable specs

## Role

- Narrative description of the agent's role.

## Inputs

- What the agent receives (user messages, documents, context).

The agent will get "initial Context" that identifies the "user role", the "brand", and any "supporting data" available about this account

## Outputs

- What the agent must produce.
agent must produce a an Onboarding conversation for capturing account data according to user role. the output is expected to be a summary of all the required fields:
- brief examples
- brand guidelines documentation
- deliverable specs for most briefed projects

## Constraints

- Global constraints, must-not rules, guardrails.
Must not accept information of other brands or other accounts

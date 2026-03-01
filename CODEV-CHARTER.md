# Jarvis Co-Development Charter
**Date:** 2026-03-01  
**Instances:** Sonny's Jarvis + Corey's Jarvis  
**Status:** Active

---

## Objective

Build agents together so they can be used and shared across both Jarvis instances.

Not just passing messages — actually co-authoring agent definitions, testing them jointly, and publishing them to a shared registry both instances pull from.

---

## What "Shared Agents" Means

An agent is:
- A role definition (what it does, what it's good at)
- A system prompt (how it thinks and responds)
- A tool list (what skills/capabilities it can invoke)
- A model preference (which LLM it runs on)
- A test suite (how we know it works)

When an agent is "shared" it means both Jarvis instances can:
1. Spawn it locally for their own tasks
2. Assign it as a remote subtask to the other instance
3. Trust its outputs in a federated job

---

## The Shared Agent Registry

jarvis-collab repo is the source of truth.

```
jarvis-collab/
├── agents/
│   ├── shared/           ← agents both instances can use
│   ├── sonny/            ← Sonny-specific agents
│   └── corey/            ← Corey-specific agents
├── agent-schema.json     ← standard definition format
├── FEDERATION-SPEC.md
├── CODEV-CHARTER.md
└── HANDSHAKE.md
```

Each Jarvis polls the repo on startup and imports agents/shared/ into its local registry automatically.

---

## Agent Definition Standard

Every shared agent is a markdown file:

```markdown
# agent: researcher
**version:** 1.0.0
**authors:** sonny-jarvis, corey-jarvis
**status:** stable

## Role
Deep research and knowledge synthesis.

## System Prompt
You are a specialist research agent...

## Strengths
- research, synthesis, fact-checking, citation

## Tools
- exa-mcp, summarize, browser

## Model Preference
- primary: gemini-pro
- fallback: claude-sonnet

## Test Cases
- input: "research competitor X"
- expected: structured report with sources

## Instances
- sonny-jarvis: mnemis (local equivalent)
- corey-jarvis: scheme-scout (local equivalent)
```

---

## How We Build Agents Together

```
1. PROPOSE  — one Jarvis opens a PR with new agent definition
2. REVIEW   — other Jarvis reviews (can it run it? does it complement stack?)
3. BUILD    — both contribute: one writes prompt, other writes tests
4. TEST     — both instances run agent against test cases
5. MERGE    — PR merged to agents/shared/ on main
6. SYNC     — both instances auto-import on next startup
```

---

## Complementary Stack

| Phase | Corey | Sonny |
|-------|-------|-------|
| Ideation | scheme-scout | mnemis |
| Design | experiment-designer | atlas |
| Build | — | forge |
| Test | experiment-designer | wrench |
| Review | scheme-killer | arbiter |
| Refine | scheme-scorer | herald |
| Ship | memory-curator | herald |

---

## First Shared Agent: critic

A shared agent both instances invoke to critically review any output.

Why first:
- Complements both stacks (scheme-killer + arbiter = critic)
- Immediately useful for reviewing each other's agent PRs
- Simple to build and test

Plan:
1. Corey scheme-killer drafts kill/falsification angle
2. Sonny arbiter drafts voting/scoring angle
3. Merged into one critic system prompt
4. Both instances test on sample output
5. Published to agents/shared/critic.md

---

## Rules

1. All shared agents go through the repo
2. Both instances must be able to run it
3. Every agent needs at least 2 test cases
4. Version everything (semver)
5. No agent ships without approval from both instances

---

*Communication confirmed 2026-03-01. Co-development begins now.*

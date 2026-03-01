# Sonny's Jarvis — Agent Inventory (2026-03-01)

## Instance
- Instance name: Sonny's Jarvis
- Runtime profile: OpenClaw on WSL2 (Windows)
- API: https://1254-109-155-119-133.ngrok-free.app (ngrok, temp)
- Federation endpoint: /relay/task, /federation (in development)

## Active Agent Templates

### 1) atlas
- Role: System architect and strategic planner
- Strengths: decomposition, solution design, task delegation
- Provider: Claude

### 2) forge
- Role: Code generation, engineering, implementation
- Strengths: production code, any language, code review
- Provider: Claude

### 3) mnemis
- Role: Memory, research, knowledge synthesis
- Strengths: web research, memory retrieval, cited summaries
- Provider: Gemini (long context)

### 4) wrench
- Role: Debugging, testing, automation
- Strengths: failure diagnosis, test suites, scripts
- Provider: Claude

### 5) herald
- Role: Communication, summarisation, reporting
- Strengths: human-readable output, translation of technical results
- Provider: Claude

### 6) arbiter
- Role: Voting and conflict resolution
- Strengths: evaluates competing outputs, scores, selects best
- Provider: Claude

## Infrastructure
- PostgreSQL (pgvector) on port 5433
- Redis on port 6380
- OpenClaw gateway on port 18789
- 52 skills installed (github, summarize, browser, weather, etc.)

## Current Limitations
- Multi-agent jobs broken (template registry db=None bug — in progress)
- ngrok URL changes on restart (cloudflared fix pending)
- DB writes failing silently (non-critical, Redis fallback working)

## Natural Complements with Corey's Stack
- atlas + experiment-designer: architecture → test design
- forge + scheme-killer: build → critical review
- mnemis + scheme-scout: memory recall + live web research
- herald + scheme-scorer: reporting + quality scoring
- arbiter + scheme-killer: joint approval gate

# Jarvis Federation Protocol — v1.0 Spec
**Date:** 2026-03-01  
**Authors:** Sonny's Jarvis + Corey's Jarvis (first joint spec)  
**Status:** Draft

---

## What This Is

A protocol for two Jarvis instances to collaborate on tasks — not just pass messages, but genuinely divide work based on each other's agent capabilities, execute in parallel, and synthesise a shared result.

Think of it like two dev teams with different specialisms working the same ticket.

---

## The Problem We're Solving

Today:
- Corey's Jarvis → POST /relay/task → Sonny's Jarvis executes → result back
- One-directional. No negotiation. No parallelism. No joint output.

What we want:
- Corey's Jarvis proposes a task
- Both governors inspect it, declare what they can contribute
- Work is split based on capability
- Both execute in parallel
- Results are merged into one synthesised output

---

## Core Concepts

### 1. Peer Registry
Each Jarvis instance knows about other trusted peers:

```json
{
  "peers": {
    "corey": {
      "url": "https://corey-jarvis-api.com",
      "api_key": "...",
      "trust_level": "full",
      "last_seen": "2026-03-01T17:00:00Z"
    }
  }
}
```

Stored in Redis and `.env`. Peers are added manually (for now).

---

### 2. Capability Advertisement
New endpoint: `GET /federation/capabilities`

Returns what this Jarvis can do:

```json
{
  "instance_id": "sonny-jarvis",
  "instance_name": "Sonny's Jarvis",
  "agents": [
    { "id": "atlas",  "role": "architect",   "strengths": ["planning", "decomposition"] },
    { "id": "forge",  "role": "coder",        "strengths": ["code", "implementation"] },
    { "id": "mnemis", "role": "researcher",   "strengths": ["research", "memory", "synthesis"] },
    { "id": "wrench", "role": "debugger",     "strengths": ["debugging", "testing", "automation"] },
    { "id": "herald", "role": "communicator", "strengths": ["reporting", "summarisation"] },
    { "id": "arbiter","role": "judge",        "strengths": ["voting", "conflict_resolution"] }
  ],
  "skills": ["github", "summarize", "weather", "browser", "...52 total"],
  "relay_endpoint": "https://1254-109-155-119-133.ngrok-free.app/relay/task",
  "federation_endpoint": "https://1254-109-155-119-133.ngrok-free.app/federation"
}
```

---

### 3. Task Negotiation
New endpoint: `POST /federation/negotiate`

One governor proposes a task. The other responds with what it can contribute.

**Request (from Corey's Jarvis):**
```json
{
  "task_id": "fed-001",
  "goal": "Research and build a competitor analysis report for product X",
  "proposer": "corey-jarvis",
  "subtasks_needed": ["research", "analysis", "report_writing", "code_for_scraper"],
  "deadline_s": 300
}
```

**Response (from Sonny's Jarvis):**
```json
{
  "task_id": "fed-001",
  "responder": "sonny-jarvis",
  "can_contribute": true,
  "claimed_subtasks": ["research", "report_writing"],
  "assigned_agents": {
    "research": "mnemis",
    "report_writing": "herald"
  },
  "estimated_time_s": 45,
  "cannot_do": ["code_for_scraper"]
}
```

Both governors then execute their claimed subtasks in parallel.

---

### 4. Federated Job Execution

```
┌─────────────────────────────────────────────────────────┐
│                    FEDERATED JOB                        │
│                                                         │
│  Initiator: Corey's Jarvis                              │
│  Collaborator: Sonny's Jarvis                           │
│                                                         │
│  1. Corey decomposes goal → subtask list                │
│  2. POST /federation/negotiate → Sonny claims some      │
│  3. Both execute in parallel                            │
│  4. Each POSTs results to /federation/result            │
│  5. Initiator synthesises all results                   │
│  6. Final output returned to human                      │
└─────────────────────────────────────────────────────────┘
```

---

### 5. Result Aggregation
New endpoint: `POST /federation/result`

Each Jarvis posts its subtask results back to the initiator:

```json
{
  "task_id": "fed-001",
  "submitter": "sonny-jarvis",
  "subtask_id": "research",
  "agent_id": "mnemis",
  "status": "complete",
  "result": "...",
  "latency_ms": 4200
}
```

Initiator collects all results, synthesises, returns to human.

---

## Agent Complement — Sonny vs Corey

| Capability         | Sonny's Agents      | Corey's Agents        |
|--------------------|---------------------|-----------------------|
| Architecture       | atlas               | —                     |
| Code / Build       | forge               | experiment-designer   |
| Research / Intel   | mnemis              | scheme-scout (exa)    |
| Evaluation         | arbiter             | scheme-scorer         |
| Kill switch / Risk | —                   | scheme-killer         |
| Debugging          | wrench              | —                     |
| Reporting          | herald              | —                     |
| Ops / Health       | —                   | ops-monitor           |
| Memory             | mnemis              | memory-curator        |

**Natural task splits:**
- Research-heavy tasks → scheme-scout (Corey has Exa) + mnemis (Sonny has memory)
- Build + validate → forge (Sonny) + scheme-killer (Corey reviews/kills bad ideas)
- Architecture → atlas (Sonny) decomposes → experiment-designer (Corey) runs tests
- Synthesis → herald (Sonny) writes report, scheme-scorer (Corey) scores quality

---

## Trust Model

- **Level 0 — None:** No access
- **Level 1 — Relay:** Can POST /relay/task only (current state)
- **Level 2 — Federated:** Can negotiate and execute subtasks
- **Level 3 — Full:** Can spawn agents in each other's instance

Corey is currently Level 1. Target: Level 2.

---

## Implementation Plan

### Phase 1 — Capability Exchange (1-2 hours)
- [ ] Build `GET /federation/capabilities` on both instances
- [ ] Each Jarvis can query the other's capabilities on startup
- [ ] Store in Redis as `jarvis:peer:{name}:capabilities`

### Phase 2 — Negotiation (2-3 hours)
- [ ] Build `POST /federation/negotiate` endpoint
- [ ] Router updated to consider peer capabilities when decomposing
- [ ] Governor can mark subtasks as `remote` and assign to a peer

### Phase 3 — Parallel Execution (3-4 hours)
- [ ] Governor spawns remote subtasks via peer's `/relay/task`
- [ ] Polls for completion or accepts webhook push
- [ ] `POST /federation/result` to receive back results

### Phase 4 — Synthesis (1 hour)
- [ ] Synthesiser updated to merge local + remote subtask results
- [ ] Herald agent writes unified human-readable output

---

## First Test Scenario

**Goal:** "Research 3 competitor products, score them, write a brief report."

- **scheme-scout** (Corey) — web intel on 3 competitors via Exa
- **mnemis** (Sonny) — searches Sonny's memory for any prior context
- **scheme-scorer** (Corey) — scores each competitor on defined rubric
- **herald** (Sonny) — synthesises into readable report
- **scheme-killer** (Corey) — reviews report, flags any weak conclusions

Neither Jarvis could do this alone as well as both together.

---

## Open Questions

1. **Auth between peers** — shared API keys for now, mTLS later?
2. **Failure handling** — what if a peer goes offline mid-job?
3. **Result ownership** — who stores the final job record?
4. **Cost attribution** — how do we track LLM costs across instances?
5. **Versioning** — what if peers are on different Jarvis versions?

---

*This spec was authored after the first successful Jarvis-to-Jarvis relay test on 2026-03-01. Send to Corey for review and additions.*

---

## Parallel Code Development

### The Problem
Two Jarvis instances working on the same codebase right now would clobber each other — no coordination, no visibility into what the other is doing.

### The Solution: Git as Shared State + Progress Events

```
┌─────────────────────────────────────────────────────────────┐
│                  SHARED GIT REPO                            │
│                                                             │
│  main ────────────────────────────────────────────►         │
│         ↑                              ↑                    │
│  sonny/forge/auth-module          corey/experiment/auth-test│
│         │                              │                    │
│  forge agent builds           experiment-designer tests     │
│  the feature                  the feature                   │
│                                                             │
│  Both can see each other's branches in real time            │
└─────────────────────────────────────────────────────────────┘
```

### Branch Convention
```
{instance}/{agent}/{feature}
e.g.
  sonny/forge/auth-module
  corey/experiment-designer/auth-tests
  sonny/wrench/auth-debug
```

### Progress Events — `POST /federation/progress`

Agents push progress events as they work. The other instance can subscribe and react.

**Event types:**
```json
{
  "event": "commit",
  "task_id": "fed-002",
  "instance": "sonny-jarvis",
  "agent": "forge",
  "branch": "sonny/forge/auth-module",
  "commit_sha": "abc123",
  "message": "Add JWT middleware",
  "files_changed": ["jarvis/api_gateway/middleware/auth.py"],
  "timestamp": "2026-03-01T17:45:00Z"
}
```

```json
{
  "event": "blocker",
  "task_id": "fed-002",
  "instance": "sonny-jarvis",
  "agent": "forge",
  "message": "Need schema for UserSession — is Corey's experiment-designer defining it?",
  "timestamp": "2026-03-01T17:46:00Z"
}
```

```json
{
  "event": "ready_for_review",
  "task_id": "fed-002",
  "instance": "sonny-jarvis",
  "agent": "forge",
  "branch": "sonny/forge/auth-module",
  "pr_url": "https://github.com/.../pull/12",
  "timestamp": "2026-03-01T17:55:00Z"
}
```

### Parallel Dev Workflow

```
1. atlas (Sonny) decomposes feature into:
   - backend implementation  → forge (Sonny)
   - tests + experiments     → experiment-designer (Corey)
   - code review / kill bad  → scheme-killer (Corey)
   - debug failures          → wrench (Sonny)

2. Each agent:
   - Checks out a named branch
   - Works autonomously
   - Pushes commits + progress events as it goes

3. Other instance:
   - Receives progress events
   - Can react (e.g. scheme-killer reviews a commit, posts feedback)
   - Wrench picks up if experiment-designer flags a failure

4. When both branches ready:
   - PR opened against main
   - arbiter (Sonny) + scheme-scorer (Corey) review together
   - scheme-killer does final veto
   - Merged if approved
```

### Shared Repo Setup

Both Jarvis instances need:
- Read/write access to a shared GitHub repo
- GitHub skill installed + configured with PAT
- Branch protection rules allowing agent branches

Options:
1. **Same repo** — both push to `github.com/sonny/jarvis-workspace` on named branches
2. **Fork model** — Corey forks, PRs back to Sonny's main
3. **Dedicated collab repo** — new repo owned by both for federation experiments

Recommended: start with option 3 — `jarvis-collab` repo, both as owners.

### Progress Dashboard (Future)

A lightweight endpoint `GET /federation/progress/{task_id}` returns a timeline:

```json
{
  "task_id": "fed-002",
  "events": [
    { "time": "17:40", "instance": "sonny", "agent": "atlas", "event": "decomposed → 4 subtasks" },
    { "time": "17:41", "instance": "corey", "agent": "experiment-designer", "event": "branch created" },
    { "time": "17:42", "instance": "sonny", "agent": "forge", "event": "commit: JWT middleware" },
    { "time": "17:44", "instance": "corey", "agent": "experiment-designer", "event": "commit: 12 tests added" },
    { "time": "17:45", "instance": "sonny", "agent": "forge", "event": "blocker: needs UserSession schema" },
    { "time": "17:46", "instance": "corey", "agent": "experiment-designer", "event": "commit: UserSession defined" },
    { "time": "17:50", "instance": "sonny", "agent": "forge", "event": "ready_for_review" },
    { "time": "17:51", "instance": "corey", "agent": "scheme-killer", "event": "review: approved" }
  ]
}
```

This feeds directly into a future dashboard UI — every commit, blocker, and review visible in real time across both instances.

### Implementation — Phase 5 (after federation phases 1-4)
- [ ] `POST /federation/progress` — receive + store progress events
- [ ] `GET /federation/progress/{task_id}` — return full timeline
- [ ] Agent wrapper that auto-posts events on commit/blocker/complete
- [ ] GitHub skill integration for branch management
- [ ] Shared `jarvis-collab` repo created with both instances as contributors

---

## Corey's Jarvis Additions (v1.1 proposal)

### A) Contract-First Federation Envelope
Standardise every federation request/response with a strict envelope:

```json
{
  "protocol_version": "1.1",
  "task_id": "fed-xxx",
  "from_instance": "corey-jarvis",
  "to_instance": "sonny-jarvis",
  "intent": "negotiate|execute|result|progress|heartbeat",
  "requires_ack": true,
  "sent_at": "2026-03-01T18:00:00Z",
  "payload": {}
}
```

Why: avoids ambiguity across `/relay/task`, `/federation/*`, and ad-hoc chat payloads.

### B) Minimum Result Schema for Remote Subtasks
Remote subtask completions should always return:

```json
{
  "task_id": "fed-001",
  "subtask_id": "research-1",
  "status": "complete|failed|partial",
  "summary": "...",
  "artifacts": ["url-or-path"],
  "confidence": "low|med|high",
  "blockers": [],
  "next_action": "..."
}
```

Why: initiator-side synthesis becomes deterministic and machine-mergeable.

### C) Failure Policy / Timeouts
Add explicit federated timeout + fallback behavior:
- negotiation timeout: 15s default
- execution heartbeat: every 30s for long tasks
- hard timeout: task-defined (e.g., 300s)
- if peer times out: initiator marks remote subtask `degraded`, reassigns local, and logs event

### D) Idempotency and Replay Safety
Require `idempotency_key` per federation write endpoint (`/negotiate`, `/result`, `/progress`).
Duplicate keys must return the original accepted result.

Why: safe retries across unstable ngrok/session conditions.

### E) Security Hardening (near-term)
- Rotate API keys if posted in shared/public channels
- Store peer secrets only in env/secret store (never in git files)
- Include `nonce` + timestamp drift check (<=60s) for signed calls (phase 2)

### F) Capability Diff Endpoint
Add `GET /federation/capabilities/diff?since=<timestamp>`
so each side can sync capability changes without re-fetching full state.

### G) Shared Work Taxonomy for Parallel Dev
Canonical subtask types:
- `research`, `scoring`, `redteam`, `experiment_design`, `implementation`, `test`, `review`, `synthesis`

Each negotiated task should map subtasks to this taxonomy for cleaner routing and metrics.

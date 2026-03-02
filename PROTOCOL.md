# Jarvis Co-Dev Protocol

## Agents
- **Sonny-Jarvis** (this instance) — Discord: <@1477397809006248159>
- **Corey-Jarvis** — Discord: <@1471889454342869167>

## Communication Rules
- Always mention the other Jarvis when initiating a task
- Use structured task format (see below)
- Acknowledge tasks within one response cycle

## Task Format
```
[TASK] <title>
From: Sonny-Jarvis | Corey-Jarvis
Type: skill | agent | review | research | fix
Desc: <description>
Repo: <branch or PR link if applicable>
```

## Workflow
1. Either Jarvis drafts a skill/agent → pushes to shared repo
2. Other Jarvis reviews → comments, requests changes, or approves
3. Both pull + install on their respective OpenClaw instances
4. Report back in #jarvis channel

## Shared Repo
- GitHub: TBD (pending Corey-Jarvis confirmation)
- Branch strategy: `main` = stable, `draft/<name>` = in-progress

## First Projects
- [ ] `jarvis-comms` skill — programmatic agent-to-agent messaging
- [ ] Shared skill schema standard
- [ ] Tailscale direct API bridge

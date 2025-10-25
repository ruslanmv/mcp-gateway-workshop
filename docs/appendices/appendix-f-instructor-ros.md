# Appendix F — Instructor Run-of-Show (Minute-by-Minute)

## Day-1 AM — Theory (4h)
| Time        | Segment                | Cues & Expected State                      |
| ----------- | ---------------------- | ------------------------------------------ |
| 00:00–00:10 | Welcome & goals        | Outcomes, repo map, docs open              |
| 00:10–00:30 | Why gateway            | Pain points; UI concepts; value            |
| 00:30–01:10 | Architecture deep dive | Flow; plugin hooks; multitenancy; ADRs     |
| 01:10–01:25 | ADR highlights         | 3 decisions + trade-offs                   |
| 01:25–01:35 | Break                  | —                                          |
| 01:35–02:05 | Agents & runtimes      | CrewAI vs LangGraph; tool provider pattern |
| 02:05–02:30 | Clients & UX           | Demo MCP CLI + Inspector                   |
| 02:30–02:55 | Serving patterns       | curl passthrough demo                      |
| 02:55–03:05 | Break                  | —                                          |
| 03:05–03:30 | Deployment models      | Compose vs K8s; rollback                   |
| 03:30–03:50 | Security overview      | RBAC, OAuth/mTLS, teams                    |
| 03:50–04:00 | Observability primer   | Log fields & IDs                           |

## Day-1 PM — Labs (4h)
| Time        | Segment | Cues                           | Outputs                    |
| ----------- | ------- | ------------------------------ | -------------------------- |
| 00:00–00:20 | Lab 0   | Verify env; unblock ports      | Checklist complete         |
| 00:20–01:05 | Lab 1   | mcpgateway up; `/health`       | Health + tools screenshots |
| 01:05–01:15 | Break   | —                              | —                          |
| 01:15–02:00 | Lab 2   | Register server; invoke        | Tool appears; valid output |
| 02:00–02:35 | Lab 3   | Two clients call same tool     | 2 screenshots              |
| 02:35–02:45 | Break   | —                              | —                          |
| 02:45–03:20 | Lab 4   | Wrapper/passthrough demo       | JSON response              |
| 03:20–03:50 | Lab 5   | Enable rate limit; show 429    | 429 + 200 proofs           |
| 03:50–04:00 | Retro   | Collect blockers; tee up Day-2 | Exit tickets               |

## Day-2 AM — Theory (4h)
| Time        | Segment              | Cues                                   | State           |
| ----------- | -------------------- | -------------------------------------- | --------------- |
| 00:00–00:10 | Recap & rubric       | Success checklist                      | Clear target    |
| 00:10–00:25 | Intro & architecture | Diagram Langflow↔Adapter↔Gateway↔Agent | Shared model    |
| 00:25–00:40 | Setup & prereqs      | Dry-run commands                       | Ready to start  |
| 00:40–01:10 | Design Langflow tool | Define I/O schema; talk latency        | Flow chosen     |
| 01:10–01:20 | Break                | —                                      | —               |
| 01:20–01:50 | Expose as MCP server | Show adapter skeleton & registration   | Endpoints known |
| 01:50–02:20 | Design CrewAI agent  | Minimal code; invoke via gateway       | Code plan ready |
| 02:20–02:40 | Hardening plan       | Pick policies + RBAC; optional OBO     | Acceptance plan |
| 02:40–02:50 | Break                | —                                      | —               |
| 02:50–03:20 | Failure/rollback     | Error modes; blue/green for adapter    | Risk plan ready |
| 03:20–03:50 | Demo plan & rubric   | Proofs to collect                      | Demo script     |
| 03:50–04:00 | Q&A                  | Clarify open items                     | Confidence high |

## Day-2 PM — Labs (4h)
| Time        | Segment           | Cues                              | Outputs          |
| ----------- | ----------------- | --------------------------------- | ---------------- |
| 00:00–00:15 | Lab A: Setup      | Compose up; venv; install deps    | Ready checklist  |
| 00:15–00:55 | Lab B: Langflow   | Endpoint responds                 | Sample JSON      |
| 00:55–01:25 | Lab C: MCP expose | Register adapter; catalog visible | Tool + CLI proof |
| 01:25–01:35 | Break             | —                                 | —                |
| 01:35–02:10 | Lab D: CrewAI     | Run agent; confirm tool call      | Agent output     |
| 02:10–02:40 | Lab E: Guardrails | Show 429 + redaction              | Policy proofs    |
| 02:40–02:50 | Break             | —                                 | —                |
| 02:50–03:20 | Lab F: RBAC/(OBO) | 200 vs 403; optional OBO          | Authz + logs     |
| 03:20–03:40 | Lab G: Trace      | Correlation ID + latency          | 3‑line trace     |
| 03:40–04:00 | Team demos        | 3–4 min/team; rubric scoring      | All proofs in    |

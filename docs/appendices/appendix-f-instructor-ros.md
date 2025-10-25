# Appendix F — Instructor Run-of-Show (Minute-by-Minute)

> All times are **local**. Morning **Theory** starts at **9:00 AM** and afternoon **Labs** start at **2:00 PM**.

---

## Day-1 AM — Theory (4h) · 9:00–13:00
| Time            | Segment                                   | Cues & Expected State                       |
| --------------- | ----------------------------------------- | ------------------------------------------- |
| **09:00–09:10** | Welcome & goals                           | Outcomes, repo map, docs open               |
| **09:10–09:30** | 3.1 What is MCP and Why a Gateway         | Pain points; UI concepts; value             |
| **09:30–10:20** | 3.2 Architecture and Core Concepts        | Flow; plugin hooks; multitenancy            |
| **10:20–10:30** | Break                                     | —                                           |
| **10:30–11:35** | 3.3 Agents & Clients Overview             | CrewAI vs LangGraph; Demo MCP CLI           |
| **11:35–12:10** | 3.4 Serving Patterns: gRPC, REST, Wrappers| `curl` passthrough demo                     |
| **12:10–12:20** | Break                                     | —                                           |
| **12:20–12:50** | 3.5 Security & Governance Essentials      | RBAC, OAuth/mTLS, teams                     |
| **12:50–13:00** | 3.6 Observability & Telemetry             | Log fields & IDs; OpenTelemetry             |

---

## Day-1 PM — Labs (4h) · 14:00–18:00
| Time            | Segment                                   | Cues                            | Outputs                     |
| --------------- | ----------------------------------------- | --------------------------------| --------------------------- |
| **14:00–14:20** | 4.1 Lab 0: Environment Checks             | Verify env; unblock ports       | Checklist complete          |
| **14:20–15:05** | 4.2 Lab 1: Quickstart (Gateway Up + Well-Known) | `mcpgateway` up; `/health` | Health + tools screenshots  |
| **15:05–15:15** | Break                                     | —                               | —                           |
| **15:15–16:00** | 4.3 Lab 2: Register Your First MCP Server | Register server; invoke         | Tool appears; valid output  |
| **16:00–16:35** | 4.4 Lab 3: Clients & CLI Flows            | Two clients call same tool      | 2 screenshots               |
| **16:35–16:45** | Break                                     | —                               | —                           |
| **16:45–17:20** | 4.5 Lab 4: Simple Passthrough / Wrapper   | Wrapper/passthrough demo        | JSON response               |
| **17:20–18:00** | 4.6 Lab 5: Guardrails (Rate Limit)        | Enable rate limit; show 429     | 429 + 200 proofs            |

---

## Day-2 AM — Theory (4h) · 9:00–13:00
| Time            | Segment                                   | Cues                                    | State            |
| --------------- | ----------------------------------------- | --------------------------------------- | ---------------- |
| **09:00–09:10** | 5.1 Capstone Overview & Success Criteria  | Success checklist                       | Clear target     |
| **09:10–09:25** | 5.2 Introduction & Architecture           | Diagram Langflow↔Adapter↔Gateway↔Agent  | Shared model     |
| **09:25–09:40** | 5.3 Setup & Prerequisites                 | Dry-run commands                        | Ready to start   |
| **09:40–10:20** | 5.4 Designing the Langflow Tool (I/O and API) | Define I/O schema; talk latency     | Flow chosen      |
| **10:20–10:30** | Break                                     | —                                       | —                |
| **10:30–11:10** | 5.5 Exposing Langflow as an MCP Tool Server| Show adapter skeleton & registration    | Endpoints known  |
| **11:10–12:00** | 5.6 The CrewAI Agent Pattern              | Minimal code; invoke via gateway        | Code plan ready  |
| **12:00–12:10** | Break                                     | —                                       | —                |
| **12:10–12:50** | 5.7 Hardening: Guardrails, RBAC, (OBO), Logs | Pick policies + RBAC; optional OBO   | Acceptance plan  |
| **12:50–13:00** | Q&A                                       | Clarify open items                      | Confidence high  |

---

## Day-2 PM — Labs (4h) · 14:00–18:00
| Time            | Segment                                   | Cues                             | Outputs           |
| --------------- | ----------------------------------------- | -------------------------------- | ----------------- |
| **14:00–14:15** | 6.1 Lab A: Setup & Prereqs                | Compose up; venv; install deps   | Ready checklist   |
| **14:15–14:55** | 6.2 Lab B: Build the Langflow Tool        | Endpoint responds                | Sample JSON       |
| **14:55–15:25** | 6.3 Lab C: Expose as MCP Tool Server      | Register adapter; catalog visible| Tool + CLI proof  |
| **15:25–15:35** | Break                                     | —                                | —                 |
| **15:35–16:10** | 6.4 Lab D: Build the CrewAI Agent         | Run agent; confirm tool call     | Agent output      |
| **16:10–16:40** | 6.5 Lab E: Guardrails in Action           | Show 429 + redaction             | Policy proofs     |
| **16:40–16:50** | Break                                     | —                                | —                 |
| **16:50–17:20** | 6.6 Lab F: RBAC (+ Optional OBO)          | 200 vs 403; optional OBO         | Authz + logs      |
| **17:20–17:40** | 6.7 Lab G: Observability Trace            | Correlation ID + latency         | 3-line trace      |
| **17:40–18:00** | 6.8 Team Demos & Rubric                   | 3–4 min/team; rubric scoring     | All proofs in     |

[← Back to Syllabus](../syllabus.md){ .md-button .md-button--secondary }
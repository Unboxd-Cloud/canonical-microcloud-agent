# Canonical MicroCloud Agent Spec

## 1. Objective

- Primary goal: help platform operators plan, validate, and execute Canonical MicroCloud lifecycle work through a controlled agent and workflow boundary.
- Target operator or user: platform engineer, SRE, DevOps engineer, or infrastructure architect responsible for a MicroCloud environment.
- Primary environment: lab, staging, and production Canonical MicroCloud clusters running on on-prem or edge infrastructure.

## 2. Agent Boundary

- The agent decides: intent classification, clarification questions, workflow selection, tool selection, execution summaries, and operator-facing recommendations.
- The workflow executes: ordered bootstrap, node join, upgrade, backup, restore, drift review, and incident-response flows.
- External automation executes: `microcloud` CLI actions, `ansible` playbooks, `terraform` plans and applies, and `lxc` inspection commands.
- Human operator approves: any mutating production action, credential-dependent step, destructive recovery action, or rollback with user-visible impact.

## 3. Supported Tasks

- Cluster bootstrap planning
- Node join and expansion guidance
- Upgrade planning and verification
- Backup and restore orchestration
- Incident triage and recovery guidance
- Cost, capacity, and migration recommendations
- Environment health summaries
- Pre-change validation and post-change verification

## 4. Explicit Non-Goals

- Direct secret storage inside the agent
- Unapproved destructive production actions
- Ad hoc infrastructure mutation without workflow or audit
- Long-lived infrastructure state management inside the model runtime

## 5. Runtime Model

- Agent runtime: Microsoft Agent Framework agent for conversational routing, context gathering, and tool selection.
- Workflow runtime: Microsoft Agent Framework workflow for deterministic, approval-gated execution paths.
- Hosting model: durable Azure Functions hosting for resumable long-running workflows unless the environment requires another host.
- Session/state model: short-lived agent session state plus durable workflow checkpoints keyed by environment, request, and operator identity.

## 6. Tool Adapters

| Tool | Purpose | Read-only or mutating | Approval required |
|------|---------|-----------------------|-------------------|
| `microcloud` | Bootstrap, join, status, cluster lifecycle checks | Both | For mutating actions |
| `lxc` | Host and instance inspection, low-level diagnostics | Mostly read-only | Only for mutating host actions |
| `ansible` | Repeatable operational procedures and day-2 tasks | Both | For mutating actions |
| `terraform` | Declared infrastructure planning and controlled changes | Both | For apply or destroy |

## 7. Approval Model

- Auto-allowed: inventory reads, topology inspection, dry-run planning, fact gathering, validation checks, log collection, and status queries.
- Requires human approval: bootstrap, node join, upgrade execution, backup restore execution, Terraform apply, Ansible changes against shared environments, and recovery actions that change workload state.
- Blocked actions: secret exfiltration, credential rewriting without explicit request, destructive cluster teardown, and production mutations without an approval token.

## 8. Failure Handling

- Retry policy: retry only idempotent read or validation steps automatically; require explicit workflow policy for writes.
- Timeout policy: fail fast for interactive checks, use workflow timeouts for long-running operations, and surface partial results with the blocked step.
- Rollback or containment path: every mutating workflow must define prechecks, stop conditions, rollback steps, and operator escalation instructions.
- Operator escalation path: return the failing step, command context, logs, and recommended next action to the named operator or platform on-call.

## 9. Observability

- Logs: structured per-step logs with request ID, environment, workflow, tool, and actor.
- Traces: workflow and tool spans linked to the initiating session.
- Audit trail: immutable record of request, approval, executed commands, exit status, and rollback actions.
- Success and failure metrics: workflow completion, approval latency, rollback rate, validation failure rate, and mean time to operator confirmation.

## 10. Delivery Plan

1. Define tool contracts and environment assumptions.
2. Build the workflow for one high-value path.
3. Add approval gates for mutating actions.
4. Add validation and rollback steps.
5. Add tracing, logging, and operator-facing summaries.

## 11. Validation

- Dry-run path tested: required for bootstrap planning, upgrade planning, and Terraform plan review.
- Failure path tested: required for workflow interruption, tool failure, and approval denial.
- Approval path tested: required for all mutating workflows.
- Rollback path tested: required for upgrade, restore, and infrastructure change workflows.


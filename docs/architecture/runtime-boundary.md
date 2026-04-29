# Runtime Boundary

## Control Plane Split

Use the agent for reasoning and the workflow for execution control.

- Agent responsibilities: classify requests, gather missing context, select the correct workflow, summarize outcomes, and recommend next actions.
- Workflow responsibilities: sequence steps, wait for approvals, persist checkpoints, enforce retries, and stop on policy failures.
- Tool adapter responsibilities: translate a single workflow step into a concrete `microcloud`, `lxc`, `ansible`, or `terraform` command contract.
- Human responsibilities: approve risky actions, provide environment-specific credentials, and make incident judgment calls.

## Default Workflow Set

- `bootstrap_cluster`
- `join_node`
- `upgrade_cluster`
- `backup_cluster`
- `restore_cluster`
- `assess_health`
- `triage_incident`

## State Model

Persist only what is operationally necessary:

- environment identifier
- request identifier
- operator identity
- selected workflow
- approval state
- last successful step
- validation artifacts

Do not store raw credentials or secret material in agent session memory.

## Design Rules

- Keep infrastructure mutation outside free-form model reasoning.
- Require approval before any shared-environment write.
- Emit a verification step after every mutation.
- Make rollback explicit before execution begins.


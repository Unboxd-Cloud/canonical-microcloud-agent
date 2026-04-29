# MicroCloud Operator Workflows

## `assess_health`

1. Read environment inventory.
2. Gather cluster and host status.
3. Run validation checks.
4. Summarize health findings.

## `upgrade_cluster`

1. Validate target environment and current version.
2. Gather pre-upgrade facts.
3. Generate operator plan and rollback steps.
4. Wait for approval.
5. Execute upgrade workflow.
6. Run post-upgrade validation.
7. Publish summary and next actions.

## `restore_cluster`

1. Confirm incident context and recovery target.
2. Validate backup availability.
3. Produce containment and rollback notes.
4. Wait for approval.
5. Execute restore steps.
6. Validate service recovery.
7. Escalate if recovery validation fails.


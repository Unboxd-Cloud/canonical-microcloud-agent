# Approval Model

## Automatic Actions

- Health checks
- Inventory reads
- Log collection
- Dry-run planning
- Terraform plan review
- Ansible fact gathering

## Approval-Gated Actions

- MicroCloud bootstrap and cluster expansion
- Upgrade execution
- Backup restore execution
- Ansible write operations
- Terraform apply or destroy
- Host-level LXC mutations

## Blocked Actions

- Production-destructive action without explicit approval
- Secret extraction or export
- Credential rotation not requested by the operator
- Unscoped command execution outside defined adapters

## Approval Record

Each mutating workflow should record:

- request ID
- approver identity
- environment
- requested action
- execution timestamp
- final outcome


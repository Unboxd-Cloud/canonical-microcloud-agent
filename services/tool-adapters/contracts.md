# Tool Adapter Contracts

## `microcloud`

- Read-only operations:
  - cluster status
  - node inventory
  - version and lifecycle checks
- Mutating operations:
  - bootstrap
  - join
  - upgrade
- Required inputs:
  - environment
  - target node or cluster scope
  - approval token for writes

## `lxc`

- Read-only operations:
  - host inspection
  - instance status
  - storage and network diagnostics
- Mutating operations:
  - limited host or instance actions when wrapped by workflow policy
- Required inputs:
  - host target
  - diagnostic scope
  - approval token for writes

## `ansible`

- Read-only operations:
  - inventory checks
  - fact gathering
  - dry-run playbook validation
- Mutating operations:
  - operational playbook execution
- Required inputs:
  - inventory path
  - playbook or role target
  - limit or tag scope
  - approval token for writes

## `terraform`

- Read-only operations:
  - validate
  - fmt check
  - plan
  - show plan summary
- Mutating operations:
  - apply
  - destroy
- Required inputs:
  - environment
  - workspace or directory
  - plan file where applicable
  - approval token for writes

## `github`

- Read-only operations:
  - authentication status
  - repository inspection
- Mutating operations:
  - none in the current agent implementation

## `vscode`

- Read-only operations:
  - version inspection
  - extension listing
- Mutating operations:
  - none in the current agent implementation

## `docker`

- Read-only operations:
  - version inspection
  - daemon information
- Mutating operations:
  - none in the current agent implementation

## `snap`

- Read-only operations:
  - version inspection
  - installed snap listing
- Mutating operations:
  - none in the current agent implementation

## `playwright`

- Read-only operations:
  - version inspection
- Mutating operations:
  - none in the current agent implementation

## `canvas`

- Read-only operations:
  - version inspection
- Mutating operations:
  - none in the current agent implementation

## `openid-connect` / `oauth2`

- Read-only operations:
  - OIDC discovery
  - OAuth2 client credentials token retrieval
- Mutating operations:
  - none in the current agent implementation

## `openapi`

- Read-only and write-capable operations:
  - generic HTTP request execution against a configured OpenAPI-compatible endpoint
- Required inputs:
  - base URL
  - optional bearer token
  - method
  - path
  - optional query, headers, and JSON body

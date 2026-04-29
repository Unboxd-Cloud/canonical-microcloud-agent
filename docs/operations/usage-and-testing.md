# Usage and Testing

## Health check

```bash
cd /Users/apple/canonical-microcloud-agent
PYTHONPATH=src python3 -m microcloud_agent health
```

This reports:

- approval state
- active binary and remote transport configuration
- tool availability from the current environment

## Workflow planning

Generate a plan without executing commands:

```bash
PYTHONPATH=src python3 -m microcloud_agent plan assess_health --environment lab
PYTHONPATH=src python3 -m microcloud_agent plan bootstrap_cluster --environment lab
PYTHONPATH=src python3 -m microcloud_agent plan upgrade_cluster --environment staging
```

## Workflow execution

Run a read-only workflow:

```bash
PYTHONPATH=src python3 -m microcloud_agent run assess_health --environment lab
```

Run an approval-gated workflow:

```bash
MICROCLOUD_AGENT_APPROVAL=approved PYTHONPATH=src python3 -m microcloud_agent run upgrade_cluster --environment staging
```

## Test suite

Run the default test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

This includes:

- policy tests
- runner tests
- workflow tests
- integration test discovery

The `testcontainers` integration test skips automatically when Docker is unavailable from the current environment.

## Integration test

Run the container-backed integration test directly:

```bash
PYTHONPATH=src python3 -m unittest tests.test_testcontainers_integration -v
```

This test starts an Alpine container, injects a small `lxc` stub, and verifies the agent can execute the remote `lxc` path through the configured transport wrapper.

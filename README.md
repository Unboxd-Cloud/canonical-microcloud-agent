# AGenNext Microcloud Architect v1

AGenNext Microcloud Architect v1 is a consultative operations agent for MicroCloud environments.

It helps operators inspect host context, recommend suitable MicroCloud configurations, and guide installation and management through approval-gated workflows. The agent is designed to be contextual, goal-oriented, and operator-friendly: it assesses the environment first, asks only the missing questions, remembers preferences, and then executes deterministic infrastructure steps with explicit confirmation.

## What It Does

- Assesses MicroCloud and host state
- Recommends a suitable setup path for the current machine
- Helps install the MicroCloud stack
- Guides single-node or multi-node configuration
- Supports ongoing operational workflows
- Remembers operator preferences and recent goals
- Keeps mutating actions approval-gated

## Core Capabilities

- Consultative setup flow
- Host context inspection
- Deterministic workflow planning and execution
- Approval-gated infrastructure changes
- Local CLI mode
- Long-running API mode
- Docker deployment
- Remote execution via SSH-style operator bridges
- Lightweight operator memory
- Chat-style guidance for capability discovery

## How It Works

The intended operating model is:

1. Install the agent first
2. Ask the agent to assess the host and recommend a setup path
3. Confirm the missing configuration decisions
4. Approve the mutating workflows
5. Let the agent install, configure, and manage MicroCloud

The agent is built to avoid blind automation. It does not assume topology, interface choice, or storage configuration without operator confirmation.

## Runtime Modes

AGenNext Microcloud Architect v1 supports:

- Direct CLI mode
- API / Agent Kernel mode
- Docker deployment
- Snap packaging scaffold when packaged in your environment

## Example Use Cases

- Prepare a host for MicroCloud
- Install the MicroCloud snap stack
- Bootstrap a single-node environment
- Add a node to a multi-node environment
- Assess tooling and runtime readiness
- Guide operators through safe operational changes

## Key Design Principles

- Contextual: inspects the real host before recommending actions
- Goal-oriented: works backward from the operator’s outcome
- Approval-gated: mutating steps require explicit approval
- Polite: communicates clearly and respectfully
- Deterministic: workflows execute in a controlled, repeatable way
- Memory-backed: remembers preferences to reduce repeated questions

## Example Flow

A typical consultative setup flow looks like this:

1. Operator asks the agent to install and manage MicroCloud on the current machine
2. Agent inspects network interfaces, disks, and existing snaps
3. Agent recommends a likely topology and next workflow
4. Agent asks for any unresolved decisions
5. Operator confirms
6. Agent runs the approved install and configuration workflows

## Docker Usage

This image is intended to provide the agent runtime in a containerized form.

Typical usage pattern:

- run the container
- invoke the consultative setup flow
- confirm recommendations
- execute approved workflows

If your deployment uses a wrapper script or compose file, keep the image reference aligned with this repository.

## Intended Audience

- Platform operators
- Edge infrastructure teams
- MicroCloud administrators
- Automation engineers who still want human approval at decision points

## Important Notes

- This agent is not intended to make uncontrolled production changes
- Infrastructure mutations remain approval-gated
- Final operational safety depends on how you configure runtime access, credentials, and approval boundaries

## Summary

AGenNext Microcloud Architect v1 is not just a script runner. It is a contextual MicroCloud operations agent built to help humans figure out the right path first, then execute it safely.

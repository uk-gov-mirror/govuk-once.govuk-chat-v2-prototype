# Agent development tools

Standalone repository tooling for developing agents that run on AWS Bedrock
AgentCore Runtime. Each supported agent has an `agentcore/agentcore.json`
manifest under its directory in `services/`. Pass that directory's name to the
commands below, for example `example-agent`.

## Prerequisites

- `source scripts/dev-prepare.zsh` from the repository root, for dependencies
  and AWS credentials. Agents call real AWS services (models, memory) even
  when they run locally.
- Deploy the agent's stack with its `scripts/cdk-deploy.sh`. The deploy records
  the stack outputs the tooling reads, so run it at least once per clone, and
  again after switching `ENVIRONMENT`.

## Run an agent locally

From the repository root:

```shell
./scripts/agent-dev.sh run <agent>
```

This starts the agent as a local process with hot reload and opens the
AgentCore Inspector in the browser, where you can chat with the agent and
view its traces and resources.

If the Inspector can't render the agent's response protocol, leave that
process running and send it a prompt from a second terminal:

```shell
./scripts/agent-dev.sh run <agent> "a prompt"
```

## Invoke a deployed agent

```shell
./scripts/agent-dev.sh invoke <agent> "a prompt"
```

This sends the prompt to the agent's AgentCore Runtime in AWS rather than
running the code locally.

Both commands regenerate the AgentCore CLI's local configuration from the
recorded stack outputs, so there is nothing to re-run after a deploy.

## Add a new agent

1. Write `services/<agent>/agentcore/agentcore.json`, following an existing
   agent's as a template.
2. Create the agent's CDK stack and instantiate it in `cdk/bin/app.ts`. It
   must output `AgentRuntimeArn`, `AgentRuntimeRoleArn`, `ShortTermMemoryId`
   and `ShortTermMemoryArn`.
3. Add `services/<agent>/scripts/cdk-deploy.sh`, following an existing
   agent's script.
4. Deploy the stack, then `./scripts/agent-dev.sh run <agent>`.

## Deployment

CDK is the only thing that deploys AWS resources from this repository. The
tooling always passes the AgentCore CLI's `--skip-deploy` flag; don't use the
CLI's own `deploy` and `import` commands.

## Development

Run the checks CI runs with:

```shell
./scripts/dev-checks.sh
```

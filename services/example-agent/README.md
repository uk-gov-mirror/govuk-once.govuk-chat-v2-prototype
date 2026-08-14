# Example agent

A quick example of an LLM agent intended to be run on AWS Bedrock AgentCore
Runtime.

## Usage

Deploy the agent's infrastructure with:

```
./scripts/cdk-deploy.sh
```

Then run it locally or invoke the deployed runtime with the repo-wide agent
dev tooling — see [utilities/agent-dev](../../utilities/agent-dev/README.md).

The Inspector can't display this agent's responses because it uses this
repository's custom event format rather than AG-UI. The agent still runs, and
the traces and resources views work. To see a response, send a prompt from a
second terminal while the agent is running. From the repository root:

```
./scripts/agent-dev.sh run example-agent "Hello agent"
```

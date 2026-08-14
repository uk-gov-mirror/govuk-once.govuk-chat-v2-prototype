# AG-UI agent

A quick example of an AgentCore agent that outputs AG-UI events.

## Usage

Deploy the agent's infrastructure with:

```
./scripts/cdk-deploy.sh
```

Then run it locally or invoke the deployed runtime with the repo-wide agent
dev tooling — see [utilities/agent-dev](../../utilities/agent-dev/README.md).

The Inspector renders this agent's replies as streaming text, because it
outputs AG-UI events.

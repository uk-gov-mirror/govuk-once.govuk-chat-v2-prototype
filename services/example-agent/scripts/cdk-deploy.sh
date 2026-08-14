#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

${PROJECT_DIR}/../../scripts/check-dev-aws-credentials.sh

cd "$PROJECT_DIR/../../cdk"

# Record the stack outputs for the agent-dev command to read, instead of
# it querying CloudFormation.
pnpm exec cdk deploy ExampleAgentStack \
  --outputs-file "$PROJECT_DIR/agentcore/cdk-outputs.json" \
  "$@"

import json
import os
from pathlib import Path

import pytest

from agent_dev import configure

ACCOUNT = "123456789012"
REGION = "eu-west-2"
RUNTIME_ID = "example_agent-abc123"
RUNTIME_ARN = f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT}:runtime/{RUNTIME_ID}"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/example-agent-runtime-role"
MEMORY_ID = "example_agent_memory-abc123"
MEMORY_ARN = f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT}:memory/{MEMORY_ID}"

STACK_OUTPUTS = {
    "AgentRuntimeArn": RUNTIME_ARN,
    "AgentRuntimeRoleArn": ROLE_ARN,
    "ShortTermMemoryId": MEMORY_ID,
    "ShortTermMemoryArn": MEMORY_ARN,
}
MANIFEST_WITH_MEMORY = {
    "runtimes": [{"name": "ExampleAgent"}],
    "memories": [{"name": "ExampleAgentMemory", "eventExpiryDuration": 90}],
}


def make_service_dir(tmp_path: Path, outputs: dict[str, str] | None) -> Path:
    service_dir = tmp_path / "repo/services/example-agent"
    agentcore_dir = service_dir / "agentcore"
    agentcore_dir.mkdir(parents=True)
    if outputs is not None:
        (agentcore_dir / "cdk-outputs.json").write_text(
            json.dumps({"chaecramb-govuk-chat-ExampleAgentStack": outputs})
        )
    return service_dir


def test_missing_manifest_names_the_expected_path(tmp_path: Path) -> None:
    service_dir = make_service_dir(tmp_path, outputs=None)

    with pytest.raises(configure.ConfigError, match="example-agent has no manifest"):
        configure.read_manifest(service_dir)


def test_prepares_agentcore_configuration_from_cdk_outputs(tmp_path: Path) -> None:
    service_dir = make_service_dir(tmp_path, STACK_OUTPUTS)

    configure.prepare_agent_configuration(service_dir, MANIFEST_WITH_MEMORY)

    assert (service_dir / "agentcore/.env.local").read_text() == (
        f"BEDROCK_AGENTCORE_MEMORY_ID={MEMORY_ID}\n"
    )
    assert os.readlink(service_dir / ".venv") == "../../.venv"
    assert json.loads((service_dir / "agentcore/aws-targets.json").read_text()) == [
        {"name": "default", "account": ACCOUNT, "region": REGION}
    ]
    assert json.loads(
        (service_dir / "agentcore/.cli/deployed-state.json").read_text()
    ) == {
        "targets": {
            "default": {
                "resources": {
                    "runtimes": {
                        "ExampleAgent": {
                            "runtimeId": RUNTIME_ID,
                            "runtimeArn": RUNTIME_ARN,
                            "roleArn": ROLE_ARN,
                        }
                    },
                    "memories": {
                        "ExampleAgentMemory": {
                            "memoryId": MEMORY_ID,
                            "memoryArn": MEMORY_ARN,
                        }
                    },
                }
            }
        }
    }


def test_missing_outputs_says_deploy_first(tmp_path: Path) -> None:
    service_dir = make_service_dir(tmp_path, outputs=None)

    with pytest.raises(configure.ConfigError, match="No CDK outputs found"):
        configure.prepare_agent_configuration(service_dir, MANIFEST_WITH_MEMORY)


def test_can_prepare_configuration_repeatedly(tmp_path: Path) -> None:
    service_dir = make_service_dir(tmp_path, STACK_OUTPUTS)

    configure.prepare_agent_configuration(service_dir, MANIFEST_WITH_MEMORY)
    configure.prepare_agent_configuration(service_dir, MANIFEST_WITH_MEMORY)

    link = service_dir / ".venv"
    assert link.is_symlink()
    assert os.readlink(link) == "../../.venv"

import argparse
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from agent_dev.configure import (
    ConfigError,
    prepare_agent_configuration,
    read_manifest,
    runtime_name,
)

REPOSITORY = Path(__file__).resolve().parents[4]


def parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an agent locally or invoke its deployed runtime."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    run_parser = subparsers.add_parser(
        "run", help="Run an agent locally and open the Inspector"
    )
    run_parser.add_argument("agent", help="Agent service directory name")
    run_parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Optional prompt to send to an already-running local agent",
    )
    invoke_parser = subparsers.add_parser(
        "invoke", help="Send a prompt to an agent's deployed runtime"
    )
    invoke_parser.add_argument("agent", help="Agent service directory name")
    invoke_parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Prompt and any additional AgentCore invoke options",
    )
    return parser.parse_args(arguments)


def agentcore_command(
    action: Literal["run", "invoke"],
    runtime: str,
    arguments: list[str],
) -> list[str]:
    if action == "run":
        # --skip-deploy because CDK owns all AWS resources
        subcommand = ["dev", "--runtime", runtime, "--skip-deploy"]
    else:
        subcommand = ["invoke", "--runtime", runtime]
    return ["pnpm", "exec", "agentcore", *subcommand, *arguments]


def main() -> None:
    args = parse_args()

    credentials_check = subprocess.run(
        [str(REPOSITORY / "scripts/check-dev-aws-credentials.sh")], check=False
    )
    if credentials_check.returncode:
        sys.exit(credentials_check.returncode)

    service_dir = REPOSITORY / "services" / args.agent
    try:
        manifest = read_manifest(service_dir)
        prepare_agent_configuration(service_dir, manifest)
    except ConfigError as error:
        sys.exit(f"Error: {error}")

    command = agentcore_command(args.action, runtime_name(manifest), args.arguments)
    os.chdir(service_dir)
    os.execvp(command[0], command)

from agent_dev import cli


def test_builds_local_run_command() -> None:
    assert cli.agentcore_command("run", "ExampleAgent", []) == [
        "pnpm",
        "exec",
        "agentcore",
        "dev",
        "--runtime",
        "ExampleAgent",
        "--skip-deploy",
    ]


def test_builds_deployed_invoke_command() -> None:
    command = cli.agentcore_command(
        "invoke",
        "AguiAgent",
        ["How do I renew my passport?", "--session-id", "session-123"],
    )

    assert command == [
        "pnpm",
        "exec",
        "agentcore",
        "invoke",
        "--runtime",
        "AguiAgent",
        "How do I renew my passport?",
        "--session-id",
        "session-123",
    ]

from types import SimpleNamespace

import pytest
from ag_ui.core import (
    RunFinishedEvent,
    RunStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
)
from agui_agent.main import app, invoke


def input_data():
    return {
        "threadId": "session-123",
        "runId": "run-456",
        "state": {},
        "messages": [{"role": "user", "content": "Tell me a joke", "id": "msg-1"}],
        "tools": [],
        "context": [
            {"description": "actorId", "value": "actor-123"},
        ],
        "forwardedProps": [],
    }


async def fake_agui_stream():
    yield RunStartedEvent(
        thread_id="session-123",
        run_id="run-456",
    )

    yield TextMessageStartEvent(
        message_id="msg-1",
        role="assistant",
    )

    yield TextMessageContentEvent(
        message_id="msg-1",
        delta="Knock knock",
    )

    yield TextMessageContentEvent(
        message_id="msg-1",
        delta="Who's there?",
    )

    yield TextMessageEndEvent(
        message_id="msg-1",
    )

    yield RunFinishedEvent(
        thread_id="session-123",
        run_id="run-456",
    )


def test_app_has_entrypoint():
    assert app is not None
    assert hasattr(app, "entrypoint")


@pytest.mark.asyncio
async def test_invoke_yields_agui_events(mocker):
    mock_strands_agent = mocker.Mock()
    mock_strands_agent.run = mocker.Mock(return_value=fake_agui_stream())

    mocker.patch(
        "agui_agent.main.StrandsAgent",
        return_value=mock_strands_agent,
    )
    mocker.patch("agui_agent.main.Agent")
    mocker.patch("agui_agent.main.BedrockModel")
    mocker.patch("agui_agent.main.AgentCoreMemorySessionManager")
    mocker.patch("agui_agent.main.AgentCoreMemoryConfig")

    mocker.patch.dict(
        "agui_agent.main.os.environ",
        {"BEDROCK_AGENTCORE_MEMORY_ID": "my-memory-123"},
    )

    context = SimpleNamespace(session_id="test-session")

    result = []
    async for event in invoke(input_data(), context):
        result.append(event)

    assert result == [
        RunStartedEvent(
            thread_id="session-123",
            run_id="run-456",
        ),
        TextMessageStartEvent(
            message_id="msg-1",
            role="assistant",
        ),
        TextMessageContentEvent(
            message_id="msg-1",
            delta="Knock knock",
        ),
        TextMessageContentEvent(
            message_id="msg-1",
            delta="Who's there?",
        ),
        TextMessageEndEvent(
            message_id="msg-1",
        ),
        RunFinishedEvent(
            thread_id="session-123",
            run_id="run-456",
        ),
    ]


@pytest.mark.asyncio
async def test_memory_config_uses_default_session_id(mocker):
    config = mocker.patch("agui_agent.main.AgentCoreMemoryConfig")

    mock_strands_agent = mocker.Mock()
    mock_strands_agent.run = mocker.Mock(return_value=fake_agui_stream())

    mocker.patch(
        "agui_agent.main.StrandsAgent",
        return_value=mock_strands_agent,
    )

    mocker.patch("agui_agent.main.Agent")
    mocker.patch("agui_agent.main.BedrockModel")
    mocker.patch("agui_agent.main.AgentCoreMemorySessionManager")

    mocker.patch.dict(
        "agui_agent.main.os.environ",
        {"BEDROCK_AGENTCORE_MEMORY_ID": "my-memory-123"},
    )

    context = SimpleNamespace()

    async for _ in invoke(input_data(), context):
        break

    _, kwargs = config.call_args

    assert kwargs["session_id"] == "default-session"


@pytest.mark.asyncio
async def test_invoke_raises_error_if_no_actor_id_in_context(mocker):
    context = SimpleNamespace()

    with pytest.raises(ValueError, match="No actor_id found in context"):
        async for _ in invoke({}, context):
            pass

import os
from collections.abc import AsyncGenerator

from ag_ui.core import BaseEvent, RunAgentInput
from ag_ui_strands import StrandsAgent, StrandsAgentConfig
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from govuk_chat_v2_prototype_private import load_prompts
from strands import Agent
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload, context) -> AsyncGenerator[BaseEvent]:
    session_id = getattr(context, "session_id", None) or "default-session"

    payload_context = payload.get("context", {})
    actor_id = next(
        (c["value"] for c in payload_context if c["description"] == "actorId"), None
    )

    if actor_id is None:
        raise ValueError("No actorId found in context")

    memory_config = AgentCoreMemoryConfig(
        memory_id=os.environ["BEDROCK_AGENTCORE_MEMORY_ID"],
        session_id=session_id,
        actor_id=actor_id,
    )

    with AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name="eu-west-1",
    ) as session_manager:
        prompts = load_prompts()
        structured_answer_prompt = prompts["structured_answer_composer"][
            "system_prompt"
        ]

        model = BedrockModel(
            model_id="eu.anthropic.claude-sonnet-5", max_tokens=4000, temperature=0.0
        )

        agent = Agent(
            model=model,
            system_prompt=structured_answer_prompt,
            session_manager=session_manager,
            tools=[],
            callback_handler=None,  # disable Strands' default callback handler which prints all events to stdout
        )

        agent_config = StrandsAgentConfig(
            # By default StrandsAgentConfig emits MESSAGES_SNAPSHOT events, which
            # assistant-ui renders as a single assistant message. It'll then render
            # the actual messages from the stream as they arrive too.
            # https://github.com/ag-ui-protocol/ag-ui/blob/11f03fa65c4fa22a8637d3f6e06e77d8c1b9ae78/integrations/aws-strands/python/src/ag_ui_strands/config.py#L112-L121
            emit_messages_snapshot=False,
        )

        agui_agent = StrandsAgent(
            agent=agent,
            name="AGUI_Agent",
            description="A helpful assistant",
            config=agent_config,
        )

        keys = (
            "threadId",
            "runId",
            "state",
            "messages",
            "tools",
            "context",
            "forwardedProps",
        )
        input_data = {k: payload[k] for k in keys}
        run_input = RunAgentInput(**input_data)

        async for event in agui_agent.run(run_input):
            yield event


if __name__ == "__main__":
    app.run()

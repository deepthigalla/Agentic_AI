import os
import asyncio
from typing import cast
from dotenv import load_dotenv

load_dotenv()

from autogen_core import event
from agent_framework import (
    ChatMessage,
    Role,
    SequentialBuilder,
    WorkflowOutputEvent,
)

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import ClientSecretCredential  # ✅ async credential

# -------------------------------------------
# Azure configuration
# -------------------------------------------
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")


async def main():
    """
    Runs a sequential multi-agent workflow:
    Summarize → Classify → Recommend action
    """

    # ---------------------------------------
    # Create ASYNC credential (ONCE)
    # ---------------------------------------
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )

    # ---------------------------------------
    # Agent instructions
    # ---------------------------------------
    summarizer_instructions = """
    Summarize the customer's feedback in one short sentence.
    Keep it neutral and concise.
    """

    classifier_instructions = """
    Classify the feedback as one of:
    - Positive
    - Negative
    - Feature request
    """

    action_instructions = """
    Based on the summary and classification,
    suggest the next action in one short sentence.
    """

    # ---------------------------------------
    # Azure AI Agent Client
    # ---------------------------------------
    async with AzureAIAgentClient(
        async_credential=credential,
        endpoint=project_endpoint,
    ) as chat_client:

        summarizer = chat_client.create_agent(
            name="summarizer",
            model=model_deployment,
            instructions=summarizer_instructions,
        )

        classifier = chat_client.create_agent(
            name="classifier",
            model=model_deployment,
            instructions=classifier_instructions,
        )

        action = chat_client.create_agent(
            name="action",
            model=model_deployment,
            instructions=action_instructions,
        )

        feedback = """
        I use the dashboard every day to monitor metrics, and it works well overall.
        But when I'm working late at night, the bright screen is really harsh on my eyes.
        If you added a dark mode option, it would make the experience much more comfortable.
        """

        workflow = (
            SequentialBuilder()
            .participants([summarizer, classifier, action])
            .build()
        )

        outputs: list[list[ChatMessage]] = []

        async for evt in workflow.run_stream(
            f"Customer feedback: {feedback}"
        ):
            if isinstance(evt, WorkflowOutputEvent):
                outputs.append(cast(list[ChatMessage], evt.data))

        if outputs:
            for i, msg in enumerate(outputs[-1], start=1):
                author = msg.author_name or (
                    "assistant" if msg.role == Role.ASSISTANT else "user"
                )
                print("-" * 60)
                print(f"{i:02d} [{author}]")
                print(msg.text)


if __name__ == "__main__":
    asyncio.run(main())

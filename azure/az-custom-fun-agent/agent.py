import os
from dotenv import load_dotenv

from azure.identity import ClientSecretCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FunctionTool,
    ToolSet,
    ListSortOrder,
    MessageRole,
)
from user_functions import user_functions


def main():
    os.system("cls" if os.name == "nt" else "clear")

    load_dotenv()

    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # ✅ Service Principal authentication
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )

    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=credential,
    )

    # Toolset
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    agent_client.enable_auto_function_calls(toolset)

    # Create agent
    agent = agent_client.create_agent(
        model=model_deployment,
        name="support-agent",
        instructions="""
You are a technical support agent.
When a user has a technical issue, ask for their email address and a description.
Use the function provided to submit a support ticket.
If a file is saved, tell the user the file name.
""",
        toolset=toolset,
    )

    thread = agent_client.threads.create()
    print(f"You're chatting with: {agent.name} ({agent.id})")

    while True:
        user_prompt = input("Enter a prompt (or type 'quit' to exit): ").strip()
        if user_prompt.lower() == "quit":
            break
        if not user_prompt:
            continue

        agent_client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_prompt,
        )

        run = agent_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        if run.status == "failed":
            print(run.last_error)
            continue

        last_msg = agent_client.messages.get_last_message_text_by_role(
            thread_id=thread.id,
            role=MessageRole.AGENT,
        )

        if last_msg:
            print(f"\nAgent: {last_msg.text.value}")

    agent_client.delete_agent(agent.id)
    print("Deleted agent")


if __name__ == "__main__":
    main()

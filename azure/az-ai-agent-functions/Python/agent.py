import os
from dotenv import load_dotenv
from azure.identity import EnvironmentCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole
from user_functions import user_functions  # Assuming this exists and is correct
from azure.identity import DefaultAzureCredential

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables
    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    if not project_endpoint or not model_deployment:
        print("Error: Missing PROJECT_ENDPOINT or MODEL_DEPLOYMENT_NAME in .env file.")
        return

    # Use EnvironmentCredential to authenticate (you must set AZURE_CLIENT_ID, TENANT_ID, SECRET)
    credential = EnvironmentCredential()

    # Create the Agents client
    agent_client = AgentsClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()

    )

    # Define an agent that can use the custom functions
    with agent_client:
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        agent_client.enable_auto_function_calls(toolset)

        agent = agent_client.create_agent(
            model=model_deployment,
            name="support-agent",
            instructions="""You are a technical support agent.
                            When a user has a technical issue, you get their email address and a description of the issue.
                            Then you use those values to submit a support ticket using the function available to you.
                            If a file is saved, tell the user the file name.
                        """,
            toolset=toolset
        )

        thread = agent_client.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")

        while True:
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if not user_prompt.strip():
                print("Please enter a prompt.")
                continue

            message = agent_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt
            )
            run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
                continue

            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            if last_msg:
                print(f"Agent: {last_msg.text.value}")

        print("\nConversation Log:\n")
        messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                print(f"{message.role}: {last_msg.text.value}\n")

        agent_client.delete_agent(agent.id)
        print("Deleted agent")

if __name__ == '__main__':
    main()

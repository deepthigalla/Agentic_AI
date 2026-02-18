import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated
from pydantic import Field

from azure.identity import ClientSecretCredential
from azure.ai.agents.aio import AgentsClient
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient


async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    load_dotenv()

    project_endpoint = os.environ["PROJECT_ENDPOINT"]

    # ✅ Service Principal authentication (SYNC is correct here)
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )

    # ✅ Create AgentsClient ONCE
    agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=credential,
    )

    # Load expenses data
    script_dir = Path(__file__).parent
    file_path = script_dir / "data.txt"
    expenses_data = file_path.read_text()

    user_prompt = input(
        f"Here is the expenses data in your file:\n\n"
        f"{expenses_data}\n\n"
        f"What would you like me to do with it?\n\n"
    )

    await process_expenses_data(user_prompt, expenses_data, agents_client)


async def process_expenses_data(prompt, expenses_data, agents_client):

    async with ChatAgent(
        chat_client=AzureAIAgentClient(
            agents_client=agents_client  # ✅ CORRECT
        ),
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="expenses_agent",
        instructions="""
You are an AI assistant for expense claim submission.
When a user submits expenses data and requests an expense claim:
1. Itemize the expenses
2. Calculate the total
3. Use the send_email tool to email expenses@contoso.com
   with subject 'Expense Claim'
4. Confirm submission to the user
""",
        tools=[send_email],  # ✅ must be a list
    ) as agent:

        messages = [f"{prompt}\n\n{expenses_data}"]
        response = await agent.run(messages)
        print(f"\n# Agent:\n{response}")


# Tool function
def send_email(
    to: Annotated[str, Field(description="Who to send the email to")],
    subject: Annotated[str, Field(description="The subject of the email")],
    body: Annotated[str, Field(description="The email body")],
):
    print("\n📧 EMAIL SENT")
    print("To:", to)
    print("Subject:", subject)
    print(body)
    print()


if __name__ == "__main__":
    asyncio.run(main())

import os
from dotenv import load_dotenv
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, ListSortOrder, MessageRole


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    script_dir = Path(__file__).parent
    file_path = script_dir / 'data.txt'

    with file_path.open('r') as f:
        data = f.read()
        print(data)

    # Create client
    credential = DefaultAzureCredential()
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=credential
    )

    with agent_client:
        # Upload file
        uploaded_file = agent_client.files.upload_and_poll(
            file_path=file_path,
            purpose=FilePurpose.AGENTS
        )

        print(f"Uploaded {uploaded_file.filename}")

        code_interpreter = CodeInterpreterTool(file_ids=[uploaded_file.id])

        # ------- FIX #1: OLD → NEW API -------
        agent = agent_client.create_agent(
            model=model_deployment,
            name="data-agent",
            instructions=(
                "You are an AI agent that analyzes the data in the uploaded file. "
                "If the user requests a chart, create it and save it as a .png file."
            ),
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )
        # -------------------------------------

        print(f"Using agent: {agent.name}")

        # ------- FIX #2: OLD → NEW API -------
        thread = agent_client.threads.create(messages=[])

        # -------------------------------------

        # REPL Loop
        while True:
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")

            if user_prompt.lower() == "quit":
                break

            if not user_prompt.strip():
                print("Please enter a prompt.")
                continue

            # ------- FIX #3: OLD → NEW API -------
            agent_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt,
            )
            # -------------------------------------

            # ------- FIX #4: OLD → NEW API -------
            run = agent_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            # -------------------------------------

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
                continue

            # ------- FIX #5: OLD → NEW API -------
            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT
            )
            # -------------------------------------

            if last_msg:
                print(f"\nAgent: {last_msg.text.value}\n")

        # Print full conversation log
        print("\nConversation Log:\n")

        # ------- FIX #6: OLD → NEW API -------
        messages = agent_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        # -------------------------------------

        for msg in messages:
            if msg.text_messages:
                last_msg = msg.text_messages[-1]
                print(f"{msg.role}: {last_msg.text.value}\n")

        # Download generated images
        for msg in messages:
            # ------- FIX #7: OLD → NEW API -------
            for img in getattr(msg, "images", []):
                file_id = img.file_id
                file_name = f"{file_id}.png"

                agent_client.files.save(file_id=file_id, file_name=file_name)
                print(f"Saved image to: {Path.cwd() / file_name}")
            # -------------------------------------

        # ------- FIX #8: OLD → NEW API -------
        agent_client.delete_agent(agent.id)
        # -------------------------------------

        print("Agent deleted.")


if __name__ == "__main__":
    main()

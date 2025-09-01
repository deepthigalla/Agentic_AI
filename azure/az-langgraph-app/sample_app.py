# main.py

from fastapi import FastAPI, Request
from langgraph.graph import StateGraph
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
import os

app = FastAPI()

# Setup Azure OpenAI
llm = AzureChatOpenAI(
    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    openai_api_version="2023-05-15",
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"]
)

# Define your LangGraph node
def respond(state):
    message = state["message"]
    response = llm([HumanMessage(content=message)])
    return {"message": response.content}

# Build LangGraph
builder = StateGraph()
builder.add_node("response", respond)
builder.set_entry_point("response")
graph = builder.compile()

# API route
@app.post("/invoke")
async def invoke(request: Request):
    data = await request.json()
    message = data.get("message", "")
    result = graph.invoke({"message": message})
    return {"response": result["message"]}

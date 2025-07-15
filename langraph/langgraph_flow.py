from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda

# Define your state schema
class MyState(TypedDict):
    input: str

# A simple function node
def say_hello(state: MyState) -> MyState:
    print(f"Hello, {state['input']}!")
    return state

# Build LangGraph
def get_langgraph():
    builder = StateGraph(MyState)  # Pass the state schema here
    builder.add_node("hello", RunnableLambda(say_hello))
    builder.set_entry_point("hello")
    return builder.compile()

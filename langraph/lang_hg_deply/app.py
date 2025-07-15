import gradio as gr
from langgraph_flow import get_langgraph

graph = get_langgraph()

def run_graph(input_text):
    result = graph.invoke({"input": input_text})
    return "Graph executed successfully."

demo = gr.Interface(fn=run_graph, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()

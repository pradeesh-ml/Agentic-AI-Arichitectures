import os
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt.tool_node import ToolNode
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agentic Architecture - ReAct"

console = Console()

# Initialize LLM and Tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool = TavilySearch(max_results=2, name="web_search")
llm_with_tools = llm.bind_tools([search_tool])

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# Define Nodes and Router
def react_agent_node(state: AgentState):
    console.print("---REACT AGENT : Thinking...---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

react_tool_node = ToolNode([search_tool])

def react_router(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        console.print("--- ROUTER: Decision is to call a tool. ---")
        return "tools"
    console.print("--- ROUTER: Decision is to finish ---")
    return "__end__"

# Build Graph
react_graph_build = StateGraph(AgentState)
react_graph_build.add_node("agent", react_agent_node)
react_graph_build.add_node("tools", react_tool_node)

react_graph_build.set_entry_point("agent")
react_graph_build.add_conditional_edges("agent", react_router, {"tools": "tools", "__end__": "__end__"})
react_graph_build.add_edge("tools", "agent")

react_agent_app = react_graph_build.compile()

# Execution
if __name__ == "__main__":
    user_query = input("Enter your query: ")
    prompt = (
    "You are a ReAct agent.\n"
    "Rules:\n"
    "- If a question involves dates, time, current events, or changing facts, "
    "you MUST call the web_search tool.\n"
    "- You are NOT allowed to answer such questions from memory.\n"
    "- Your final answer MUST be based only on tool observations.\n"
)
    if user_query:
        initial_input = {
                    "messages": [
                        ("system", prompt),
                        ("user", user_query)
                    ]
                }
        final_output = None
        
        for chunk in react_agent_app.stream(initial_input, stream_mode="values"):
            final_output = chunk
            console.print("--- [bold purple]Current State[/bold purple]")
            chunk['messages'][-1].pretty_print()
            console.print('\n')
        
        if final_output:
            console.print("\n--- [bold green]Final Output from ReAct Agent[/bold green] ---")
            console.print(Markdown(final_output['messages'][-1].text))

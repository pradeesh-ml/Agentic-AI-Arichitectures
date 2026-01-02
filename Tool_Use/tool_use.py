import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from rich.console import Console
from rich.prompt import Prompt

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agentic Architecture - Tool Use (Nebius)"

# Initialize Rich Console
console = Console()

# Define Tools
search_tool = TavilySearch(max_results=2)
search_tool.name = "web_search"
search_tool.description = "A tool that can used to search the internet for up to date information on any topic, including news, events, and current affairs"

tools = [search_tool]

# Define State
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)


# Define Nodes
def agent_node(state: AgentState):
    console.print("--- AGENT: Thinking... ---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

def final_answer_node(state: AgentState):
    console.print("[cyan]--- AGENT: Synthesizing final answer... ---[/cyan]")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Define Router
def router_function(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        console.print("[yellow]--- ROUTER: Decision is to call a tool. ---[/yellow]")
        return "call_tool"

    if isinstance(last_message, ToolMessage):
        console.print("[cyan]--- ROUTER: Tool result received. Generating final answer. ---[/cyan]")
        return "final_answer"
    else:
        console.print("[green]--- ROUTER: Decision is to finish. ---[/green]")
        return "__end__"



# Build Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("call_tool", tool_node)
graph_builder.add_node("final_answer", final_answer_node)

graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent",
    router_function,
)

graph_builder.add_edge("call_tool", "agent")
graph_builder.add_edge("final_answer", "__end__")

tool_agent_app = graph_builder.compile()

if __name__ == "__main__":
    console.print("[bold blue]Agentic AI - Tool Use Demo[/bold blue]")
    
    user_query = Prompt.ask("[bold cyan]Enter your query[/bold cyan] (or 'exit' to quit)")
        
    initial_input = {"messages": [("user", user_query)]}

    console.print(f"[bold cyan]🚀 Kicking off Tool Use workflow for request:[/bold cyan] '{user_query}'\n")
    for chunk in tool_agent_app.stream(initial_input, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
    console.print("\n---\n")

    
    console.print("\n[bold green]✅ Tool Use workflow complete![/bold green]\n")
    




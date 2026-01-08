import re
from typing import List, Annotated, Optional, TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import  ToolMessage
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()
console = Console()

tavily_search_tool = TavilySearch(max_results=2)

@tool
def web_search(query: str):
    """Performs a web search using Tavily and returns the results as a string."""
    console.print(f"--- TOOL: Searching for {query}---")
    results = tavily_search_tool.invoke(query)
    return results

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
llm_with_tools = llm.bind_tools([web_search])

class Plan(BaseModel):
    steps: List[str] = Field(description="A list of tool calls that, when executed, will answer the query.")

class PlanningState(TypedDict):
    user_request: str
    plan: Optional[List[str]]
    intermediate_steps: List[ToolMessage]
    final_answer: Optional[str]

def planner_node(state: PlanningState):
    console.print("---.PLANNER: Decomposing task... ---")
    planner_llm = llm.with_structured_output(Plan)
    prompt = f"""You are an expert planner. Your job is to create a step-by-step plan to answer the user's request.
        Each step in the plan must be a single call to the `web_search` tool.

        **Instructions:**
        1. Analyze the user's request.
        2. Break it down into a sequence of simple, logical search queries.
        3. Format the output as a list of strings, where each string is a single valid tool call.

        **Example:**
        Request: "What is the capital of France and what is its population?"
        Correct Plan Output:
        [
            "web_search('capital of France')",
            "web_search('population of Paris')"
        ]

        **User's Request:**
        {state['user_request']}
    """
    plan_result = planner_llm.invoke(prompt)
    console.print(f"---PLANNER: Generated Plan: {plan_result.steps}")
    return {'plan': plan_result.steps}

def executor_node(state: PlanningState):
    console.print("EXCUTOR: Running next step... ---")
    plan = state['plan']
    next_step = plan[0]
    match = re.search(r"(\w+)\((?:\'|\")(.*?)(?:\'|\")\)", next_step)
    if not match:
        tool_name = "web_search"
        query = next_step
    else:
        tool_name, query = match.groups()
    
    console.print(f"---EXECUTOR: Calling tool '{tool_name}' with '{query}' ---")
    result = tavily_search_tool.invoke(query)

    tool_message = ToolMessage(
        content=str(result),
        name=tool_name,
        tool_call_id=f"manual-{hash(query)}"
    )
    return {
        'plan': plan[1:],
        "intermediate_steps": state["intermediate_steps"] + [tool_message]
    }

def synthesizer_node(state: PlanningState):
    console.print("--- SYNTHESIZER: Generating final answer... ---")
    context = "\n".join([f"Tool {msg.name} returned {msg.content}" for msg in state['intermediate_steps']])
    prompt = f"""You are an expert synthesizer. Based on the user's request and the collected data, provide a comprehensive final answer.
    
    Request: {state['user_request']}
    Collected Data:
    {context}
    """
    final_answer = llm.invoke(prompt).content
    return {"final_answer": final_answer}

def planning_router(state: PlanningState):
    if not state['plan']:
        console.print("--- ROUTER: Plan complete. Moving to synthesizer. ---")
        return "synthesize"
    else:
        console.print("--- ROUTER: Plan has more steps. Continuing execution. ---")
        return "execute"

planning_graph_builder = StateGraph(PlanningState)
planning_graph_builder.add_node("plan", planner_node)
planning_graph_builder.add_node("execute", executor_node)
planning_graph_builder.add_node("synthesize", synthesizer_node)

planning_graph_builder.set_entry_point("plan")
planning_graph_builder.add_conditional_edges("plan", planning_router, {"execute": "execute", "synthesize": "synthesize"})
planning_graph_builder.add_conditional_edges("execute", planning_router, {"execute": "execute", "synthesize": "synthesize"})
planning_graph_builder.add_edge("synthesize", END)

planner_agent_app = planning_graph_builder.compile()

if __name__ == "__main__":
    user_input = input("Enter your request: ")
    console.print(f"[bold green]Testing PLANNING agent on the query:[/bold green] '{user_input}'\n")

    initial_input = {"user_request": user_input, "intermediate_steps": []}

    final_planning_output = planner_agent_app.invoke(initial_input)
    console.print("\n--- [bold green]Final Output from Planning Agent[/bold green] ---")
    console.print(Markdown(final_planning_output['final_answer']))

import os
from typing import List, TypedDict, Optional
from dotenv import load_dotenv
import json
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
console = Console()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agentic Architecture - PEV"

def flaky_web_search(query):
    """Performs a web search, but is designed to fail for a specific query."""
    console.print(f"--- TOOL: Searching for {query}... ---")
    if "employee count" in query.lower():
        console.print("--- TOOL: [bold red]Simulating API failure![/bold red] ---")
        return "Error: Could not retrieve data. The API endpoint is currently unavailable."
    else:
        result = TavilySearch(max_results=2).invoke(query)
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        return str(result)

class VerificationResult(BaseModel):
    is_successful: bool = Field(description="True if the tool execution was successful and the data is valid.")
    reasoning: str = Field(description="Reasoning for the verfication decision.")

class PEVState(TypedDict):
    user_input: str
    plan: Optional[List[str]]
    last_tool_result: Optional[str]
    intermediate_steps: List[str]
    final_answer: Optional[str]
    retries: int

class Plan(BaseModel):
    steps: List[str] = Field(description="List of queries (max 5).", max_length=5)

def planner_node(state: PEVState):
    retries = state.get("retries", 0)
    if retries > 3:
        console.print("--- (PEV) PLANNER: Retry limit reached. Stopping. ---")
        return {
            "plan": [],
            "final_answer": "Error: Unable to complete task after multiple retries."
        }
    
    console.print(f"--- (PEV) PLANNER: Creating/revising plan (retry {retries})... ---")
    planner_llm = llm.with_structured_output(Plan)
    past_context = "\n".join(state['intermediate_steps'])
    base_prompt = f"""
    You are a planning agent. 
    Create a plan to answer: '{state['user_input']}'. 
    Use the 'flaky_web_search' tool.

    Rules:
    - Return ONLY valid JSON in this exact format: {{ "steps": ["query1", "query2"] }}
    - Maximum 5 steps.
    - Do NOT repeat failed queries or endless variations.
    - Do NOT output explanations, only JSON.

    Previous attempts and results:
    {past_context}
    """
    plan = planner_llm.invoke(base_prompt)
    return {'plan': plan.steps, "retries": retries + 1}

def excutor_node(state: PEVState):
    if not state['plan']:
        console.print("--- (PEV) EXECUTOR: No steps left, skipping execution. ---")
        return {}
    console.print("--- EXECUTOR: Running next steps... ---")
    next_step = state['plan'][0]
    result = flaky_web_search(next_step)
    return {'plan': state['plan'][1:], "last_tool_result": result}

def verifier_node(state: PEVState):
    console.print("--- VERIFIER: Checking last tool result... ---")
    verifier_llm = llm.with_structured_output(VerificationResult)
    prompt = f"Verify if the following tool output is a successful result or an error message. The task was '{state['user_input']}'.\n\nTool Output: '{state['last_tool_result']}'"
    verification = verifier_llm.invoke(prompt)
    console.print(f"--- VERIFIER: Judgment is '{'Success' if verification.is_successful else 'Failure'}' ---")
    if verification.is_successful:
        return {'intermediate_steps': state['intermediate_steps'] + [state['last_tool_result']]}
    else:
        return {"plan": [], "intermediate_steps": state["intermediate_steps"] + [f"Verification Failed: {state['last_tool_result']}"]}

def synthesizer_node(state: PEVState):
    console.print("--- (Basic) SYNTHESIZER: Generating final answer... ---")
    context = "\n".join(state["intermediate_steps"])
    prompt = f"Synthesize an answer for '{state['user_input']}' using this data:\n{context}"
    answer = llm.invoke(prompt).content
    return {"final_answer": answer}

def router(state: PEVState):
    if state.get("final_answer"):
        console.print("--- ROUTER: Final answer available. Moving to synthesizer. ---")
        return "synthesize"
    if not state['plan']:
        if state["intermediate_steps"] and "Verification Failed" in state["intermediate_steps"][-1]:
            console.print("--- ROUTER: Verification failed. Re-planning... ---")
            return "plan"
        else:
            console.print("--- ROUTER: Plan complete. Moving to synthesizer. ---")
            return "synthesize"
    else:
        console.print("--- ROUTER: Plan has more steps. Continuing execution. ---")
        return "execute"

pev_graph_builder = StateGraph(PEVState)
pev_graph_builder.add_node("plan", planner_node)
pev_graph_builder.add_node("execute", excutor_node)
pev_graph_builder.add_node("verify", verifier_node)
pev_graph_builder.add_node("synthesize", synthesizer_node)

pev_graph_builder.set_entry_point("plan")
pev_graph_builder.add_edge("plan", "execute")
pev_graph_builder.add_edge("execute", "verify")
pev_graph_builder.add_conditional_edges("verify", router)
pev_graph_builder.add_edge('synthesize', END)

pev_agent_app = pev_graph_builder.compile()

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    initial_input = {"user_input": user_query, "intermediate_steps": [], "retries": 0}
    final_output = pev_agent_app.invoke(initial_input)
    console.print("\n--- [bold green]Final Output from PEV Agent[/bold green] ---")
    console.print(Markdown(final_output['final_answer']))

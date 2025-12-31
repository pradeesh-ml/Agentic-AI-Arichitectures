import os
import json
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN-PROJECT"] = "Agentic AI Architecture - Relection"

# Initialize Console
console = Console()

# --- Data Models ---

class DraftCode(BaseModel):
    code: str = Field(description="The Python code generated to solve the user's request.")
    explanation: str = Field(description="A brief explanation of how the code works.")

class Critique(BaseModel):
    has_error: bool = Field(description="Does the code have any potential bugs or logical errors?")
    is_efficient: bool = Field(description="Is the code written in an efficient and optimal way?")
    suggested_improvements: List[str] = Field(description="Specific, actionable suggestions for improving the code.")
    critique_summary: str = Field(description="A summary of the critique.")

class RefinedCode(BaseModel):
    refined_code: str = Field(description="The final, improved Python code.")
    refinement_summary: str = Field(description="A summary of the changes made based on the critique.")

# --- State Definition ---

class RefectionState(TypedDict):
    user_request: str
    draft: Optional[dict]
    critique: Optional[dict]
    refined_code: Optional[dict]

# --- LLM Initialization ---

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

# --- Graph Nodes ---

def generator_node(state):
    console.print("--- 1. Generating Initial Draft ---")
    generator_llm = llm.with_structured_output(DraftCode)
    prompt = f"""You are an expert Python programmer. Write a Python function to solve the following request.
    Provide a simple, clear implementation and an explanation.
    Request: {state['user_request']}
    """
    draft = generator_llm.invoke(prompt)
    return {'draft': draft.model_dump()}

def critic_node(state):
    console.print("--- 2. Critiquing Draft ---")
    critic_llm = llm.with_structured_output(Critique)
    code_to_critique = state['draft']['code']
    prompt = f"""You are an expert code reviewer and senior Python developer. Your task is to perform a thorough critique of the following code.
    
    Analyze the code for:
    1.  **Bugs and Errors:** Are there any potential runtime errors, logical flaws, or edge cases that are not handled?
    2.  **Efficiency and Best Practices:** Is this the most efficient way to solve the problem? Does it follow standard Python conventions (PEP 8)?
    
    Provide a structured critique with specific, actionable suggestions.
    
    Code to Review:
    ```python
    {code_to_critique}
    ```
    """
    critique = critic_llm.invoke(prompt)
    return {"critique": critique.model_dump()}

def refiner_node(state):
    console.print("--- 3. Refined Code ---")
    refiner_llm = llm.with_structured_output(RefinedCode)
    draft_code = state['draft']['code']
    critique_suggestions = json.dumps(state['critique'], indent=2)
    prompt = f"""
        You are an expert Python programmer tasked with refining a piece of code based on a critique.

        Your goal is to rewrite the original code, implementing all the suggested improvements.

        IMPORTANT RULES:
        - Do NOT use triple-quoted docstrings ("")
        - Use inline comments (#) instead of docstrings
        - Return ONLY valid Python code as plain text

        Original Code:
        ```python
        {draft_code}```

        Critique and Suggestions:
        {critique_suggestions}

        Return exactly two fields:

        refined_code

        refinement_summary
        """

    refined_code = refiner_llm.invoke(prompt)
    return {'refined_code': refined_code.model_dump()}

# --- Graph Construction ---

graph_builder = StateGraph(RefectionState)

graph_builder.add_node("generator", generator_node)
graph_builder.add_node("critic", critic_node)
graph_builder.add_node("refiner", refiner_node)

graph_builder.set_entry_point("generator")
graph_builder.add_edge("generator", "critic")
graph_builder.add_edge("critic", "refiner")
graph_builder.add_edge("refiner", END)

reflection_app = graph_builder.compile()

# --- Main Execution ---

if __name__ == "__main__":
    # Get user request
    user_request = console.input("[bold green]Enter your coding request:[/bold green] ")

    initial_input = {'user_request': user_request}

    console.print(f"[bold cyan]🚀 Kicking off Reflection workflow for request:[/bold cyan] '{user_request}'\n")

    final_state = None
    for state_update in reflection_app.stream(initial_input, stream_mode='values'):
        final_state = state_update
    
    console.print("\n[bold green]✅ Reflection workflow complete![/bold green]")

    if final_state and 'draft' in final_state and 'critique' in final_state and 'refined_code' in final_state:
        console.print(Markdown("\n---### Initial Draft ---"))
        console.print(Markdown(f"**Explanation:** {final_state['draft']['explanation']}"))
    
        console.print(Syntax(final_state['draft']['code'], "python", theme="monokai", line_numbers=True))

        console.print(Markdown("\n--- ### Critique ---"))
        console.print(Markdown(f"**Summary:** {final_state['critique']['critique_summary']}"))
        console.print(Markdown(f"**Improvements Suggested:**"))
        for improvement in final_state['critique']['suggested_improvements']:
            console.print(Markdown(f"- {improvement}"))

        console.print(Markdown("\n--- ### Final Refined Code ---"))
        console.print(Markdown(f"**Refinement Summary:** {final_state['refined_code']['refinement_summary']}"))
        console.print(Syntax(final_state['refined_code']['refined_code'], "python", theme="monokai", line_numbers=True))
    else:
        console.print("[bold red]Error: The `final_state` is not available or is incomplete. Please check the execution of the previous cells.[/bold red]")

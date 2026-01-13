import os
from typing import Optional, TypedDict
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agentic Architecture - Multi-Agent"

console = Console()
search_tool = TavilySearch(max_results=3, name="web_search")
llm_with_tools = llm.bind_tools([search_tool])

class MultiAgentState(TypedDict):
    user_input: str
    news_report: Optional[str]
    technical_report: Optional[str]
    financial_report: Optional[str]
    final_report: Optional[str]

def create_specialist_node(persona, output_key):
    """Factory function to create a specialist agent node."""
    system_prompt = persona + "\n\nYou have access to a web search tool. Your output MUST be a concise report section, formatted in markdown, focusing only on your area of expertise."
    prompt_template = ChatPromptTemplate([
        ("system", system_prompt),
        ("human", "{user_input}")
    ])

    agent = prompt_template | llm_with_tools
    
    def specialist_node(state: MultiAgentState):
        console.print(f"--- CALLING {output_key.replace('_report', '').upper()} ANALYST ---")
        result = agent.invoke({'user_input': state['user_input']})
        content = result.content if result.content else f"No direct content, tool calls: {result.tool_calls}"
        return {output_key: content}
    return specialist_node

news_analyst_node = create_specialist_node(
    "You are an expert News Analyst. Your specialty is scouring the web for the latest news, articles, and social media sentiment about a company.",
    "news_report"
)
technical_analyst_node = create_specialist_node(
    "You are an expert Technical Analyst. You specialize in analyzing stock price charts, trends, and technical indicators.",
    "technical_report"
)
financial_analyst_node = create_specialist_node(
    "You are an expert Financial Analyst. You specialize in interpreting financial statements and performance metrics.",
    "financial_report"
)

def report_writer_node(state: MultiAgentState):
    """The manager agent that synthesizes the specialist reports."""
    console.print("---CALLING REPORT WRITER ---")
    prompt = f"""You are an expert financial editor. Your task is to combine the following specialist reports into a single, professional, and cohesive market analysis report. Add a brief introductory and concluding paragraph.
    
    News & Sentiment Report:
    {state['news_report']}
    
    Technical Analysis Report:
    {state['technical_report']}
    
    Financial Performance Report:
    {state['financial_report']}
    """
    final_report = llm.invoke(prompt).content
    return {"final_report": final_report}

multi_agent_graph_builder = StateGraph(MultiAgentState)

multi_agent_graph_builder.add_node("news_analyst", news_analyst_node)
multi_agent_graph_builder.add_node("technical_analyst", technical_analyst_node)
multi_agent_graph_builder.add_node("financial_analyst", financial_analyst_node)
multi_agent_graph_builder.add_node("report_writer", report_writer_node)

multi_agent_graph_builder.set_entry_point("news_analyst")
multi_agent_graph_builder.add_edge("news_analyst", "technical_analyst")
multi_agent_graph_builder.add_edge("technical_analyst", "financial_analyst")
multi_agent_graph_builder.add_edge("financial_analyst", "report_writer")
multi_agent_graph_builder.add_edge("report_writer", END)

multi_agent_app = multi_agent_graph_builder.compile()

user_query = input("Enter your query for market analysis: ")
console.print(f"[bold green]Testing MULTI-AGENT TEAM on the same task:[/bold green]\n'{user_query}'\n")
if user_query:
    initial_multi_agent_input = {"user_input": user_query}
    final_response = multi_agent_app.invoke(initial_multi_agent_input)
    
    console.print("\n--- [bold green]Final Report from Multi-Agent Team[/bold green] ---")
    console.print(Markdown(final_response['final_report']))

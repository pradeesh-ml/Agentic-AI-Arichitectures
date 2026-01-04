# Agentic AI: ReAct (Reasoning + Acting)

This project implements a **ReAct Agent**, an agentic AI architecture where a model does not rely solely on its internal training data. Instead, it **interleaves reasoning with acting**, allowing it to use external tools (like web search) to answer questions dynamically.

The goal is to demonstrate how **AI capabilities expand when we architect systems** to interact with the real world, rather than relying on a static knowledge base.

---

## What Is ReAct in Agentic AI?

ReAct (Reasoning + Acting) is an architectural pattern where an AI system **thinks about what to do, performs an action, and observes the result** before generating a final answer.

In a traditional LLM interaction:
- The model receives a prompt (e.g., "What is the stock price of Apple?")
- It relies on "frozen" training data (which is often outdated)
- It hallucinates or declines to answer

In a ReAct Loop:
- The model **Reasons**: "I need to check the current stock price."
- The model **Acts**: It calls a search tool.
- The model **Observes**: It reads the search results.
- The model **Refines**: It formulates the answer based on the new data.

This mirrors how humans work: We don't memorize the internet; we know how to use a browser to find information when we need it.

---

## Core Logic of the ReAct Loop

The ReAct Agent implemented here follows a cyclic graph logic:

1. **Reasoning (The Agent Node)**
   The LLM analyzes the user's input and the current conversation history. It decides whether it has enough information to answer or if it needs to call a tool.

2. **Routing (The Decision)**
   A logical router inspects the Agent's output.
   - If the Agent generated a `tool_call`, the system routes to the **Tool Node**.
   - If the Agent generated a final answer, the system routes to **END**.

3. **Acting (The Tool Node)**
   If a tool was requested (in this case, `TavilySearchResults`), the system executes the actual API call and appends the results back to the conversation state.

4. **Observation**
   The Agent receives the tool output as a new message. It then re-enters the **Reasoning** phase to decide if the new information is sufficient to answer the user.

---

## Why ReAct Is Useful

ReAct significantly improves output utility in tasks where:
- **Real-time information** is required (news, weather, stocks)
- **Math or computation** is needed (using a calculator tool)
- **Accuracy is critical** and must be grounded in sources

Instead of forcing the model to be a "know-it-all," ReAct allows the model to act as a **reasoning engine** that orchestrates external capabilities.

---

## Advantages of ReAct Loops

ReAct-based systems offer several practical benefits:

- **Grounded Truth**  
  Answers are based on retrieved data rather than the model's probabilistic memory, reducing hallucinations.

- **Dynamic Capability**  
  The same agent can be upgraded simply by giving it new tools (e.g., database access, API integration) without retraining the model.

- **Transparency**  
  The "Chain of Thought" (displayed in the console) shows exactly what the agent searched for and why.

- **Self-Correction**  
  If a search yields no results, the agent can reason to try a different search term.

---

## Disadvantages and Trade-offs

ReAct is powerful but comes with trade-offs:

- **Latency**  
  The agent must wait for external API calls (e.g., web search) to complete, making it slower than a standard chat.

- **Cost and Complexity**  
  Multiple LLM hops and external API calls increase the cost per interaction.

- **Loop Limits**  
  Without safeguards, a confused agent might get stuck in an infinite loop of searching.

For this reason, ReAct is best used when **static knowledge is insufficient** for the task.

---

## How This Implementation Works

This project uses **LangGraph** to model the ReAct Loop as a state machine.

Key design choices include:

- **State Graph**: A persistent `AgentState` holds the list of messages between the user, the agent, and the tools.
- **Conditional Edges**: The `react_router` function dynamically determines the path based on the presence of `tool_calls`.
- **Tool Binding**: The Google Gemini model is explicitly aware of the `TavilySearchResults` tool signature.
- **Rich UI**: The `rich` library is used to visualize the "Thinking..." process and the final Markdown output.

The system uses Google's **Gemini Flash** for speed, as ReAct loops require low-latency inference to feel responsive.

---

## How This Differs from a Normal LLM Call

A normal LLM call looks like this:

- **User**: "Who won the game last night?"
- **LLM**: "I do not have access to real-time information." (Or it hallucinates).

This ReAct Loop differs in several key ways:

- The model **acknowledges its limitations** and decides to use a tool
- The architecture **pauses execution** to run Python code (the search)
- The model **contextualizes** the raw data into a human-readable answer
- The system is **autonomous** in its decision-making process

In other words, intelligence emerges from the **interaction between the model and its environment**.

---

## Why This Matters for Production Systems

In production environments, LLMs are rarely useful in isolation. ReAct Loops:
- Enable "RAG" (Retrieval Augmented Generation) workflows
- Allow agents to perform actions (sending emails, booking tickets)
- Create systems that stay up-to-date automatically

This pattern is the foundational block for building **autonomous agents** capable of doing actual work, rather than just talking.

---

## Final Note

This repository is part of a broader effort to explore **agentic AI architectures with real code implementations**.  
The ReAct Agent shown here serves as a bridge between static chatbots and fully autonomous systems.

The key takeaway is simple:

> Reliable AI systems are architected — not prompted.
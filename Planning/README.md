# Agentic AI: Planning

This project implements a **Planning** pattern, an agentic AI architecture that decouples "thinking" (planning) from "doing" (execution). Instead of attempting to answer a complex query in one shot, the system **decomposes the request into a sequence of actionable steps** and executes them one by one.

The goal is to demonstrate how **AI handles complexity better when it plans first**, rather than relying on a single, massive context window or chain-of-thought prompt.

---

## What Is Planning in Agentic AI?

Planning is an architectural pattern where an AI system generates a roadmap before taking any action.

In a traditional RAG or Tool-use interaction:
- The model receives a query.
- It immediately tries to pick a tool or generate an answer.
- It often gets lost if the query requires multiple distinct pieces of information.

In a Planning Loop:
- **Planner:** The model analyzes the request and creates a list of distinct tasks (e.g., "Search for X", then "Search for Y").
- **Executor:** A separate step iterates through this plan, executing tools for each item.
- **Synthesizer:** The system aggregates all gathered information to answer the original user request.

This mirrors how humans handle projects: Outline the tasks → Execute the tasks → Summarize the results.

---

## Core Logic of the Planning Agent

The architecture implemented here follows three distinct logical phases within a **LangGraph** workflow:

1. **The Planner (Decomposition)**
   The system uses an LLM with structured output (Pydantic) to break the user's request into a list of specific `web_search` tool calls.
   *   *Input:* "Compare the population of Tokyo and New York."
   *   *Plan:* `["web_search('population of Tokyo')", "web_search('population of New York')"]`

2. **The Executor (Action)**
   The system enters a loop where it:
   - Takes the first step from the plan.
   - Executes the tool (Tavily Search).
   - Stores the result in the state history.
   - Repeats until the plan is empty.

3. **The Synthesizer (Reporting)**
   Once all steps are executed, the accumulated data (intermediate steps) and the original query are passed to the LLM to generate a final, comprehensive response.

---

## Why Planning Is Useful

Planning significantly improves performance in tasks where:
- **Multi-hop reasoning is required** (e.g., "Who is the CEO of the company that acquired GitHub?").
- **Parallel data gathering is needed** (e.g., "Get stock prices for Apple, Google, and Microsoft").
- **Context is too complex** for a single search query to resolve.

Instead of hoping the model retrieves everything in one go, planning **forces a structured approach to data gathering**, ensuring no part of the question is ignored.

---

## Advantages of Planning

This architecture offers several practical benefits:

- **Divide and Conquer**  
  Complex problems become a series of simple problems. The executor only needs to solve one small task at a time.

- **Auditable Logic**  
  You can see exactly what steps the agent intends to take before it takes them.

- **Reduced Hallucination**  
  Because the final answer is based on a collection of specific tool outputs, the model relies less on its internal training data and more on retrieved context.

- **Modularity**  
  The planner can be swapped for a more advanced model, while the executor can use smaller, faster models.

---

## Disadvantages and Trade-offs

This pattern is not without costs:

- **Rigidity**  
  In this specific implementation, the plan is generated upfront. If the plan turns out to be wrong (e.g., a search fails), the agent does not currently re-plan (though advanced versions can).

- **Latency**  
  Answering a question requires at least three LLM calls (Plan + Execute + Synthesize) plus tool latency.

- **Over-engineering for Simple Queries**  
  If the user asks "Hi", generating a plan is unnecessary overhead.

---

## How This Implementation Works

This project uses **LangGraph** to manage the state and control flow.

Key design choices include:

- **Structured State:** A `TypedDict` (`PlanningState`) tracks the `plan` (future steps) and `intermediate_steps` (past results).
- **Conditional Routing:** A router checks if the plan list is empty. If not, it loops back to the executor; if yes, it moves to the synthesizer.
- **Pydantic Validation:** The planner is forced to output a valid list of strings, preventing parsing errors.
- **Rich UI:** The console output is formatted to visualize the agent's "thought process" in real-time.

---

## How This Differs from a Normal ReAct Agent

A standard ReAct (Reason + Act) agent looks like this:
- Thought: "I need to search for X." -> Action -> Observation -> Thought: "Now I need Y."

This Planning agent differs because:
- **Separation of Concerns:** The "Planning" logic is completely separated from the "Execution" logic.
- **Global View:** The planner sees the whole problem at once, whereas a ReAct agent often has "tunnel vision," only seeing the immediate next step.

In other words, this agent **knows where it is going before it starts walking.**

---

## Why This Matters for Production Systems

In production, predictability is key. Planning architectures:
- Allow developers to inspect plans for safety before execution.
- Standardize the way complex queries are handled.
- Provide a clear structure for debugging (was the plan bad, or was the tool execution bad?).

---

## Final Note

This repository is part of a broader effort to explore **agentic AI architectures with real code implementations**.  
The Planning pattern shown here provides the backbone for systems that need to perform research or execute complex workflows reliably.

The key takeaway is simple:

> Reliable AI systems are architected — not prompted.
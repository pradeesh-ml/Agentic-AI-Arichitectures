# Agentic AI: Plan-Execute-Verify (PEV) Loop

This project implements a **Plan-Execute-Verify (PEV)** architecture, an agentic workflow designed to handle tool failures and complex multi-step reasoning. Instead of blindly executing actions, this agent **plans a sequence of steps, executes them one by one, and verifies the results**, replanning dynamically if a step fails.

The goal is to demonstrate how to build **resilient AI systems** that can recover from API errors or bad data without human intervention.

---

## What Is the Plan-Execute-Verify Pattern?

The PEV pattern is an architectural approach where an AI agent breaks a high-level goal into smaller tasks and validates each step before proceeding.

In a traditional RAG or Tool-calling flow:
- The model calls a tool (e.g., search).
- The tool fails or returns irrelevant data.
- The model often hallucinates an answer or gives up.

In a PEV Loop:
- **Plan:** The agent creates a list of necessary steps.
- **Execute:** The agent performs the next specific action.
- **Verify:** A distinct reasoning step checks if the action succeeded.
- **Re-Plan:** If verification fails, the agent modifies the plan to try a different approach.

This mirrors how human engineers troubleshoot: create a strategy → try a solution → check if it worked → try a new strategy if it failed.

---

## Core Logic of the PEV Loop

The architecture implemented here follows four logical phases:

1. **Planner**
   The system analyzes the user request and previous attempts to generate a structured list of queries (steps). It explicitly avoids repeating failed steps.

2. **Executor**
   The agent takes the first step from the plan and executes it using a tool.
   *Note: This project includes a `flaky_web_search` tool designed to simulate API failures for specific queries to demonstrate the agent's resilience.*

3. **Verifier**
   The output of the tool is analyzed. The verifier decides:
   - Is this valid data?
   - Is this an error message?
   
   It returns a structured boolean judgment (`is_successful`) and reasoning.

4. **Router & Synthesizer**
   - If verified **Success**: The system records the data and continues to the next step or synthesizes the final answer.
   - If verified **Failure**: The system routes back to the **Planner** to create a new strategy based on the error.

---

## Why Verification Is Useful

Verification is critical in production environments where external dependencies are unreliable. It improves quality in scenarios involving:
- **Flaky APIs:** Endpoints that time out or return 500 errors.
- **Ambiguous Queries:** Search terms that yield no results and require rewording.
- **Hallucination Prevention:** Ensuring the model actually has the data before answering.

By decoupling **Execution** (doing the thing) from **Verification** (checking the thing), we prevent the "blind leading the blind" scenario common in simple agents.

---

## Advantages of PEV Loops

This architecture offers distinct benefits over linear chains:

- **Self-Healing**  
  The agent detects tool failures and autonomously creates a new plan to work around them.

- **Groundedness**  
  The final answer is synthesized only after data has been verified, reducing hallucinations.

- **Process Transparency**  
  The separation of planning and execution allows developers to see exactly which step failed and why.

- **Loop Limit Safety**  
  The system includes a retry limit to prevent infinite loops during hard failures.

---

## Disadvantages and Trade-offs

Like all agentic patterns, PEV comes with costs:

- **High Latency**  
  A single user query may result in 5+ LLM calls (Plan -> Execute -> Verify -> Re-Plan -> Execute -> Verify -> Synthesize).

- **Token Consumption**  
  The state (history of steps and failures) grows with every loop, increasing cost.

- **Complexity**  
  Managing the state graph and conditional routing is more complex than a standard prompt chain.

This pattern is best used for **complex research tasks** or **unreliable environments**, rather than simple conversational bots.

---

## How This Implementation Works

This project uses **LangGraph** to orchestrate the state machine.

Key design details:
- **Pydantic Models**: Used for the Planner and Verifier to ensure structured, parseable JSON outputs.
- **State Management**: A `TypedDict` tracks the `plan`, `intermediate_steps`, and `retries`.
- **Simulated Failure**: The code intentionally breaks on the query "employee count" to force the agent into a recovery loop, showcasing the replanning logic.

The workflow demonstrates that intelligence isn't just about the model's raw power, but about the **control flow** that manages the model's actions.

---

## How This Differs from a Normal LLM Call

A standard LLM with tools usually follows a `ReAct` pattern:
> "Thought -> Action -> Observation -> Answer"

The PEV Loop modifies this to:
> "Plan -> Action -> **Verification** -> **(Loop/Replanning)** -> Answer"

The difference is the **explicit check-step** and the **ability to modify the plan** mid-flight. A normal LLM often ignores a tool error and tries to answer anyway; the PEV agent refuses to proceed until the data is verified.

---

## Why This Matters for Production Systems

In real-world applications, "happy paths" are rare.
- Databases get locked.
- Search engines return garbage.
- APIs change schemas.

A **Plan-Execute-Verify** architecture transforms these runtime errors from "application crashes" into "problems to be solved," making the AI system robust enough for enterprise deployment.

---

## Final Note

This repository is part of a broader effort to explore **agentic AI architectures with real code implementations**.

The key takeaway is simple:

> Reliable AI systems are architected — not prompted.
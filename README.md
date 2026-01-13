# 🏗️ Agentic AI Architectures

This repository focuses on **architecting autonomous AI systems**, not just prompting LLMs.  
It contains **production-inspired agentic patterns** with clear logic, use cases, and implementations.

---

## 📌 Repository Overview

| Section | Description |
|------|------------|
| Goal | Move beyond prompt engineering to system-level AI design |
| Focus | Agentic architectures used in real-world applications |
| Language | Python |
| Frameworks | LangChain, LangGraph |
| Level | Intermediate → Advanced |
| Status | 🚧 Actively maintained |

---

## 🧠 Agentic Patterns Roadmap

| Pattern Name | Core Idea | When to Use | Status |
| :--- | :--- | :--- | :--- |
| **Reflection** | AI critiques and improves its own output | When accuracy & refinement matter | ✅ Done |
| **Tool Use** | Agents that call external tools | Data retrieval & automation | ✅ Done |
| **ReAct** | Combining Reasoning and Acting | Tasks requiring multi-step tool logic | ✅ Done |
| **Planning** | Pre-generating a sequence of steps | Long, complex multi-step tasks | ✅ Done |
| **Multi-Agent Systems** | Specialized agents working together | Complex workflows with distinct roles | ✅ Done |
| **PEV (Plan, Execute, Verify)** | Systematic cycle for goal accuracy | High-stakes automation | ⏳ Planned |
| **Blackboard Systems** | Agents contributing to a shared logic space | Collaborative problem solving | ⏳ Planned |
| **Episodic + Semantic Memory**| Past experiences + general knowledge | Long-term personalization & facts | ⏳ Planned |
| **Tree of Thoughts (ToT)** | Branching reasoning paths | Non-linear/Creative problem solving | ⏳ Planned |
| **Mental Loop (Simulator)** | Simulating actions before execution | Risk assessment & "rehearsal" | ⏳ Planned |
| **Meta-Controller** | Logic that manages other strategies | Generalist "master" agent systems | ⏳ Planned |
| **Graph (World-Model)** | Relationship-based memory storage | Navigating complex context/entities | ⏳ Planned |
| **Ensemble** | Voting/aggregating multiple model outputs | Reducing hallucinations & bias | ⏳ Planned |
| **Dry-Run Harness** | Sandboxed execution testing | Safe testing of destructive actions | ⏳ Planned |
| **RLHF (Self-Improvement)** | Learning from feedback loops | Continuous performance optimization | ⏳ Planned |

---


## 🛠️ Tech Stack

| Componenets | Purpose |
|-------|------|
| Python| The core programming language for the entire project. |
| LangChain | LangChain |
| LangGraph | LangGraph |
| GROQ APIs | High-performance LLMs that power the agent's reasoning. |
| Pydantic  | Ensures robust, structured data modeling, which is critical for reliable communication with LLMs. |
| Tavily Search | A powerful search API used as a tool for research-oriented agents. |
---

## 🚀 Getting Started

Follow these steps to set up the environment and run your first agentic pattern.

### 1. Clone the Repository
Begin by cloning the project to your local machine:
```bash
git clone [https://github.com/pradeesh-ml/agentic-ai-architectures.git](https://github.com/pradeesh-ml/agentic-ai-architectures.git)
cd agentic-ai-architectures
```

### 2. Environment Setup
Initialize the project and install all dependencies into a virtual environment automatically:
```bash
uv sync
```

### 3. Environment Configuration
The agents require API keys to function. Create a file named .env in the root of the project directory.

Open the .env file and add your credentials. It should look like this:
```bash
# GROQ API Key (for LLM access)
GROQ_API_KEY="your_GROQ_api_key_here"
# Gemini  API Key (for LLM access)
GOOGLE_API_KEY="your_google_api_key_here"
# LangSmith API Key (for tracing and debugging)
LANGCHAIN_API_KEY="your_langsmith_api_key_here"
# Travily API Key (for web search)
TAVILY_API_KEY="your_travily_api_key_here"
```

### 4. Run an Example
Use uv run to execute the  agent within the managed environment:
```bash
#example
uv run reflection_loops/reflection_agent.py
```


---

## 🎯 Learning Outcome

| You Will Learn |
|---------------|
| How to design agent workflows |
| When single LLM calls fail |
| How reflection improves reliability |
| How multi-agent coordination works |
| How to architect scalable AI systems |

---

## 🤝 Contributions

| Type | Welcome |
|----|--------|
| Issues | ✅ |
| Discussions | ✅ |
| Pull Requests | ✅ |

---

## 📣 Updates

New architectures and implementations will be added regularly.  
Follow the repo to stay updated ⭐


"""
langchain_style_demo.py
A minimal, runnable demo that models LangChain v0.3 concepts:
- Runnable-like components
- Planner / Orchestrator that builds a plan (chain of runnables)
- Tools invoked by Runnables
- Simple in-memory 'memory' for context
"""

from abc import ABC, abstractmethod
import random
import time

# ----------------------------
# Base Runnable (LangChain-style)
# ----------------------------
class Runnable(ABC):
    @abstractmethod
    def invoke(self, inputs, config=None, **kwargs):
        pass

# ----------------------------
# Tools (external helpers)
# ----------------------------
def tool_fetch_docs(query):
    # Fake retrieval: returns small list of "documents"
    docs = [
        f"Doc about {query} (source A)",
        f"Deep dive on {query} (source B)",
        f"Quick notes on {query} (source C)"
    ]
    time.sleep(0.2)
    return docs

def tool_call_llm(prompt):
    # Fake LLM: returns a short synthesized answer
    time.sleep(0.2)
    return f"LLM_RESPONSE: summary of '{prompt[:60]}'..."

# ----------------------------
# Runnables implementations
# ----------------------------
class RetrieverRunnable(Runnable):
    def invoke(self, inputs, config=None, **kwargs):
        q = inputs.get("query") if isinstance(inputs, dict) else inputs
        docs = tool_fetch_docs(q)
        print(f"[Retriever] fetched {len(docs)} docs for '{q}'")
        return {"query": q, "docs": docs}

class SummarizerRunnable(Runnable):
    def invoke(self, inputs, config=None, **kwargs):
        docs = inputs.get("docs", [])
        combined = " ".join(docs)
        summary = tool_call_llm(combined)
        print(f"[Summarizer] produced summary")
        return {"query": inputs.get("query"), "summary": summary}

class DecisionRunnable(Runnable):
    def invoke(self, inputs, config=None, **kwargs):
        # A tiny decision function that branches based on keywords
        summary = inputs.get("summary", "")
        if "risk" in summary.lower():
            decision = "escalate"
        else:
            decision = "respond"
        print(f"[Decision] decision -> {decision}")
        return {"query": inputs.get("query"), "decision": decision, "summary": summary}

# ----------------------------
# Planner / Orchestrator (builds simple plan)
# ----------------------------
class LangChainPlanner:
    def __init__(self, memory=None):
        self.memory = memory or {}

    def plan(self, user_query):
        # Build a simple sequence of runnables depending on query
        runnables = [RetrieverRunnable(), SummarizerRunnable(), DecisionRunnable()]
        # store plan metadata in memory
        self.memory["last_plan_for"] = user_query
        return runnables

    def execute_plan(self, runnables, inputs):
        # sequential execution (could be parallel where appropriate)
        data = inputs
        for r in runnables:
            data = r.invoke(data)
        return data

# ----------------------------
# Demo usage
# ----------------------------
def demo_langchain_style(query):
    print("\n--- LangChain-style Planner Demo ---")
    planner = LangChainPlanner(memory={})
    plan = planner.plan(query)
    result = planner.execute_plan(plan, {"query": query})
    print("\nFinal result:", result)
    print("Planner memory:", planner.memory)

if __name__ == "__main__":
    demo_langchain_style("market risk for AAPL next week")

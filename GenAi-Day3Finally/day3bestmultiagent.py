
"""
multi_agent_chatgpt_langchain_demo.py

Multi-Agent System (LangChain-style) with optional real ChatGPT integration.
- Pure-Python, no hard dependency required.
- Mode:
    USE_OPENAI = False  -> demo/mock mode (safe, reproducible)
    USE_OPENAI = True   -> will attempt to call OpenAI ChatCompletion (requires openai package and OPENAI_API_KEY)
- Agents: Retriever, Summarizer, Planner, Executor, Notifier
- Orchestrator composes agents, handles errors & fallback cleanly.
"""

import os
import time
import random
import logging
from typing import List, Dict, Any

# ---------- CONFIG ----------
USE_OPENAI = False  # set True to enable real ChatGPT calls (requires openai package + OPENAI_API_KEY)
OPENAI_MODEL = "gpt-4o-mini"  # example model name (change as needed)
# ----------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ---------- Optional OpenAI / ChatGPT client (lazy import) ----------
openai_client = None
if USE_OPENAI:
    try:
        import openai
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        openai_client = openai
        logging.info("OpenAI client loaded.")
    except Exception as e:
        logging.warning("OpenAI client not available or API key missing: %s", e)
        openai_client = None
        USE_OPENAI = False


# ---------- Utilities ----------
def safe_sleep(min_s=0.1, max_s=0.35):
    time.sleep(random.uniform(min_s, max_s))


def call_chatgpt(prompt: str, system: str = "You are a helpful assistant.") -> str:
    """
    If USE_OPENAI and client available -> call ChatGPT (OpenAI).
    Else -> return a mock deterministic reply (demo mode).
    """
    if USE_OPENAI and openai_client:
        try:
            # using chat.completions or responses -- keep generic
            response = openai_client.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=512,
                temperature=0.2,
            )
            # adapt to response shape
            content = response.choices[0].message["content"]
            return content.strip()
        except Exception as e:
            logging.error("OpenAI call failed: %s", e)
            # fallback to mock
    # Mock reply for demo/test
    safe_sleep(0.05, 0.2)
    return f"[MOCK LLM] Answer for: {prompt[:120]}"


# ---------- Agents (pure-Python) ----------
class AgentBase:
    def __init__(self, name: str):
        self.name = name

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class RetrieverAgent(AgentBase):
    """Retrieves documents or data for a query (mock or real)."""
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        logging.info("[%s] retrieving docs for query: %s", self.name, query)
        # Demo: return 3 short "documents"
        docs = [
            f"Doc A about {query} - contains summary and key points.",
            f"Doc B deep dive on {query} - includes statistics and quotes.",
            f"Doc C quick notes on {query} - short bullets.",
        ]
        safe_sleep(0.05, 0.2)
        return {"docs": docs}


class SummarizerAgent(AgentBase):
    """Summarizes a list of documents using ChatGPT (or mock)."""
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        docs: List[str] = inputs.get("docs", [])
        if not docs:
            return {"summary": ""}
        prompt = "Summarize the following documents in 3-4 concise sentences:\n\n" + "\n\n".join(docs)
        logging.info("[%s] summarizing %d docs", self.name, len(docs))
        try:
            summary = call_chatgpt(prompt)
            return {"summary": summary}
        except Exception as e:
            logging.error("[%s] summarizer error: %s", self.name, e)
            # fallback naive summary
            naive = " ".join(docs)[:400] + ("..." if len(" ".join(docs)) > 400 else "")
            return {"summary": naive}


class PlannerAgent(AgentBase):
    """Creates a plan or decision based on the summary."""
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        summary = inputs.get("summary", "")
        logging.info("[%s] planning from summary", self.name)
        # Simple plan logic: check for keywords to decide action
        lower = summary.lower()
        if "risk" in lower or "alert" in lower or "urgent" in lower:
            action = "escalate"
        elif "recommend" in lower or "buy" in lower:
            action = "trade"
        else:
            action = "inform"
        plan = {"action": action, "reason": f"decided '{action}' from summary"}
        safe_sleep(0.03, 0.12)
        return {"plan": plan}


class ExecutorAgent(AgentBase):
    """Executes actions found in the plan. Uses tools (mocked)."""
    def __init__(self, name: str):
        super().__init__(name)
        self.executions = []

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        plan = inputs.get("plan", {})
        action = plan.get("action")
        logging.info("[%s] executing action: %s", self.name, action)
        try:
            if action == "escalate":
                # simulate notifying human ops team
                result = {"status": "escalated", "ticket_id": f"TKT-{random.randint(1000,9999)}"}
            elif action == "trade":
                # simulate placing an order (mock)
                result = {"status": "traded", "order_id": f"ORD-{random.randint(10000,99999)}"}
            else:
                result = {"status": "notified", "note": "Information-only, no action taken."}
            self.executions.append(result)
            safe_sleep(0.05, 0.2)
            return {"execution": result}
        except Exception as e:
            logging.error("[%s] execution failed: %s", self.name, e)
            return {"execution": {"status": "failed", "error": str(e)}}


class NotifierAgent(AgentBase):
    """Sends final notifications (mock)."""
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        execution = inputs.get("execution", {})
        summary = inputs.get("summary", "")
        message = f"Final Result: {execution} | Summary snippet: {summary[:120]}"
        logging.info("[%s] notify -> %s", self.name, message)
        # mock sending (could call email/slack tool)
        safe_sleep(0.02, 0.06)
        return {"notified": True, "message": message}


# ---------- Orchestrator (composes agents, with error handling & fallback) ----------
class Orchestrator:
    def __init__(self):
        self.retriever = RetrieverAgent("Retriever")
        self.summarizer = SummarizerAgent("Summarizer")
        self.planner = PlannerAgent("Planner")
        self.executor = ExecutorAgent("Executor")
        self.notifier = NotifierAgent("Notifier")
        self.state = {}  # simple in-memory state

    def run(self, user_query: str) -> Dict[str, Any]:
        logging.info("[Orchestrator] start for query: %s", user_query)
        result = {"query": user_query, "steps": []}

        # Step 1: Retrieve
        try:
            out = self.retriever.run({"query": user_query})
            result["steps"].append({"retriever": out})
            self.state.update(out)
        except Exception as e:
            logging.exception("[Orchestrator] Retriever failed: %s", e)
            # fallback: empty docs
            out = {"docs": []}
            result["steps"].append({"retriever_error": str(e)})
            self.state.update(out)

        # Step 2: Summarize
        try:
            out = self.summarizer.run(self.state)
            result["steps"].append({"summarizer": out})
            self.state.update(out)
        except Exception as e:
            logging.exception("[Orchestrator] Summarizer failed: %s", e)
            # fallback: naive combined-doc summary
            docs = self.state.get("docs", [])
            naive = " ".join(docs)[:400] + ("..." if len(" ".join(docs)) > 400 else "")
            out = {"summary": naive}
            result["steps"].append({"summarizer_fallback": out})
            self.state.update(out)

        # Step 3: Plan
        try:
            out = self.planner.run(self.state)
            result["steps"].append({"planner": out})
            self.state.update(out)
        except Exception as e:
            logging.exception("[Orchestrator] Planner failed: %s", e)
            # fallback: inform
            out = {"plan": {"action": "inform", "reason": "planner_error"}}
            result["steps"].append({"planner_fallback": out})
            self.state.update(out)

        # Step 4: Execute (branching & safety)
        try:
            out = self.executor.run(self.state)
            result["steps"].append({"executor": out})
            self.state.update(out)
        except Exception as e:
            logging.exception("[Orchestrator] Executor failed: %s", e)
            # fallback: do not place orders; only notify
            out = {"execution": {"status": "skipped", "reason": "executor_error"}}
            result["steps"].append({"executor_fallback": out})
            self.state.update(out)

        # Step 5: Notify
        try:
            notify_in = {"execution": self.state.get("execution"), "summary": self.state.get("summary", "")}
            out = self.notifier.run(notify_in)
            result["steps"].append({"notifier": out})
            self.state.update(out)
        except Exception as e:
            logging.exception("[Orchestrator] Notifier failed: %s", e)
            result["steps"].append({"notifier_error": str(e)})

        logging.info("[Orchestrator] finished")
        result["final_state"] = self.state.copy()
        return result


# ---------- Demo runner ----------
def demo():
    orch = Orchestrator()

    queries = [
        "Give a concise market update for AAPL and mention any risk alerts",
        "Summarize recent KYC regulation changes affecting Indian banks",
        "Quick overview: what happened to BTC price, is there volatility?",
    ]

    for q in queries:
        print("\n" + "=" * 80)
        print(f"User Query: {q}")
        print("-" * 80)
        result = orch.run(q)
        # Pretty print a short result
        final = result.get("final_state", {})
        print("Execution summary:", final.get("trader_snapshot") or final.get("execution") or "No trade")
        print("Notification message:", final.get("last_notification") or result.get("steps")[-1])
        # For debugging print steps lightly
        for step in result["steps"]:
            print(step)
        print("=" * 80)


if __name__ == "__main__":
    demo()

"""
prod_multi_agent_orchestrator.py

Production-style simulation of multi-agent collaboration with:
- Async agents (Retriever, Enricher, Planner, Executor, Notifier)
- Tools as functions (mocked external APIs)
- Robust error handling and fallback mechanisms
- Retries with exponential backoff
- Circuit-breaker style protection for flaky tools
- State store + checkpoints (in-memory)
- Audit/logging and simple metrics
- Human-in-the-loop escalation fallback
- Idempotency keys for safe re-execution

No external dependencies. Run with: python prod_multi_agent_orchestrator.py
"""

import asyncio
import random
import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Coroutine

# -------------------------
# Logging / Audit / Metrics
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
AUDIT_LOG = []  # append dicts for audit trail
METRICS = {"flows_started": 0, "flows_failed": 0, "flows_succeeded": 0}

def audit(event: str, payload: Dict[str, Any]):
    entry = {"ts": time.time(), "event": event, "payload": payload}
    AUDIT_LOG.append(entry)
    logging.info("[AUDIT] %s %s", event, payload)

# -------------------------
# Utility: retries/backoff
# -------------------------
async def retry_async(func: Callable[..., Coroutine[Any, Any, Any]],
                      *args, retries: int = 3, initial_backoff: float = 0.2,
                      max_backoff: float = 5.0, on_retry: Optional[Callable] = None, **kwargs):
    attempt = 0
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            attempt += 1
            if attempt > retries:
                raise
            backoff = min(max_backoff, initial_backoff * (2 ** (attempt - 1)) * (0.9 + random.random() * 0.2))
            logging.warning("Retry %d/%d for %s after %.2fs due to: %s", attempt, retries, func.__name__, backoff, e)
            if on_retry:
                try:
                    on_retry(attempt, e)
                except Exception:
                    pass
            await asyncio.sleep(backoff)

# -------------------------
# Circuit Breaker (very small)
# -------------------------
@dataclass
class CircuitBreaker:
    name: str
    fail_threshold: int = 5
    recovery_timeout: float = 30.0
    _fails: int = 0
    _open_until: float = 0.0

    def record_success(self):
        self._fails = 0
        self._open_until = 0.0

    def record_failure(self):
        self._fails += 1
        if self._fails >= self.fail_threshold:
            self._open_until = time.time() + self.recovery_timeout
            logging.error("[CircuitBreaker:%s] Opened until %s", self.name, self._open_until)

    def is_open(self) -> bool:
        if self._open_until and time.time() < self._open_until:
            return True
        return False

# -------------------------
# State store / checkpoints
# -------------------------
class StateStore:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any):
        self._store[key] = value

    def get(self, key: str, default: Any = None):
        return self._store.get(key, default)

    def checkpoint(self, name: str):
        # shallow copy; in production serialize to durable storage
        self._checkpoints[name] = dict(self._store)
        logging.info("[State] checkpoint '%s' created", name)
        audit("checkpoint_created", {"name": name, "state_snapshot": list(self._store.keys())})

    def rollback(self, name: str):
        if name in self._checkpoints:
            self._store = dict(self._checkpoints[name])
            logging.info("[State] rolled back to checkpoint '%s'", name)
            audit("checkpoint_rollback", {"name": name})
        else:
            logging.warning("[State] no checkpoint '%s' to rollback", name)

# -------------------------
# Mocked external tools (I/O)
# -------------------------
async def tool_fetch_documents(query: str) -> List[str]:
    """Simulated fetcher; sometimes fails."""
    await asyncio.sleep(random.uniform(0.05, 0.3))
    if random.random() < 0.07:  # occasional failure
        raise ConnectionError("document service unavailable")
    docs = [f"Doc({query})#{i}" for i in range(1, random.randint(2, 5))]
    return docs

async def tool_call_llm(prompt: str) -> str:
    """Simulated LLM call; can be slow or fail sometimes."""
    await asyncio.sleep(random.uniform(0.1, 0.6))
    if random.random() < 0.05:
        raise RuntimeError("LLM timeout")
    return f"LLM_SUMMARY: {prompt[:120]}"

async def tool_send_alert(msg: str) -> bool:
    """Simulated notifier. Rare failures."""
    await asyncio.sleep(random.uniform(0.02, 0.1))
    if random.random() < 0.03:
        raise RuntimeError("notification service failed")
    return True

# -------------------------
# Agents (async)
# -------------------------
@dataclass
class AgentResult:
    ok: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class BaseAgent:
    def __init__(self, name: str, state: StateStore):
        self.name = name
        self.state = state

    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

class RetrieverAgent(BaseAgent):
    def __init__(self, name: str, state: StateStore, cb: CircuitBreaker):
        super().__init__(name, state)
        self.cb = cb

    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        query = payload.get("query")
        if self.cb.is_open():
            logging.warning("[%s] circuit open - skipping fetch, using cached docs", self.name)
            cached = self.state.get("cached_docs", [])
            return AgentResult(ok=True, data={"docs": cached, "source": "cache"})
        try:
            docs = await retry_async(tool_fetch_documents, query, retries=3, initial_backoff=0.2)
            self.cb.record_success()
            self.state.set("cached_docs", docs)
            audit("retriever_success", {"query": query, "docs_count": len(docs)})
            return AgentResult(ok=True, data={"docs": docs, "source": "live"})
        except Exception as e:
            self.cb.record_failure()
            logging.error("[%s] retriever failed: %s", self.name, e)
            audit("retriever_error", {"query": query, "error": str(e)})
            # fallback: return cached docs or empty list
            fallback_docs = self.state.get("cached_docs", [])
            return AgentResult(ok=False, data={"docs": fallback_docs, "source": "fallback"}, error=str(e))

class EnricherAgent(BaseAgent):
    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        docs = payload.get("docs", [])
        if not docs:
            return AgentResult(ok=False, data={"enriched": []}, error="no_docs")
        try:
            # call LLM with concatenated docs - protect prompt size in prod
            prompt = "Summarize: " + " ".join(docs[:5])
            summary = await retry_async(tool_call_llm, prompt, retries=2, initial_backoff=0.3)
            audit("enricher_success", {"docs_count": len(docs)})
            self.state.set("last_summary", summary)
            return AgentResult(ok=True, data={"summary": summary})
        except Exception as e:
            logging.error("[%s] enricher failed: %s", self.name, e)
            audit("enricher_error", {"error": str(e)})
            # fallback: naive summary (join first sentences)
            naive = " ".join(docs)[:240] + ("..." if len(" ".join(docs)) > 240 else "")
            return AgentResult(ok=False, data={"summary": naive}, error=str(e))

class PlannerAgent(BaseAgent):
    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        summary = payload.get("summary", "")
        # simple decision logic: detect risk word
        decision = "inform"
        if any(w in summary.lower() for w in ["alert", "fraud", "risk", "urgent"]):
            decision = "escalate"
        elif any(w in summary.lower() for w in ["opportunity", "buy", "recommend"]):
            decision = "recommend_trade"
        plan = {"decision": decision, "summary_snippet": summary[:200]}
        audit("planner_decision", {"decision": decision})
        self.state.set("last_plan", plan)
        return AgentResult(ok=True, data={"plan": plan})

class ExecutorAgent(BaseAgent):
    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        plan = payload.get("plan", {})
        decision = plan.get("decision")
        # Safe execution checks
        idempotency_key = payload.get("idempotency_key") or str(uuid.uuid4())
        if self.state.get(f"exec_done_{idempotency_key}"):
            logging.info("[%s] idempotent replay detected for %s - skipping", self.name, idempotency_key)
            return AgentResult(ok=True, data={"result": "already_executed", "idempotency_key": idempotency_key})
        try:
            if decision == "escalate":
                # escalate -> send alert to human ops (critical)
                await retry_async(tool_send_alert, f"ESCALATION: {plan['summary_snippet']}", retries=2)
                result = {"status": "escalated", "ticket_id": f"TKT-{random.randint(1000,9999)}"}
            elif decision == "recommend_trade":
                # simulate placing order via tool (mocked as alert)
                await retry_async(tool_send_alert, f"TRADE_EXECUTE: {plan['summary_snippet']}", retries=2)
                result = {"status": "trade_executed", "order_id": f"ORD-{random.randint(10000,99999)}"}
            else:
                result = {"status": "no_action"}
            # commit execution idempotently
            self.state.set(f"exec_done_{idempotency_key}", result)
            audit("executor_success", {"idempotency_key": idempotency_key, "result": result})
            return AgentResult(ok=True, data={"result": result, "idempotency_key": idempotency_key})
        except Exception as e:
            logging.error("[%s] executor failed: %s", self.name, e)
            audit("executor_error", {"error": str(e)})
            return AgentResult(ok=False, data={"result": None}, error=str(e))

class NotifierAgent(BaseAgent):
    async def run(self, payload: Dict[str, Any]) -> AgentResult:
        summary = payload.get("summary", "")
        exec_result = payload.get("execution_result", {})
        message = f"Notification: exec_result={exec_result} | summary={summary[:200]}"
        try:
            await retry_async(tool_send_alert, message, retries=2)
            audit("notifier_sent", {"message": message})
            return AgentResult(ok=True, data={"notified": True})
        except Exception as e:
            logging.error("[%s] notifier failed: %s", self.name, e)
            audit("notifier_failed", {"error": str(e)})
            # fallback: log and keep for retry via human-in-loop
            self.state.set("pending_notification", {"message": message, "ts": time.time()})
            return AgentResult(ok=False, data={"notified": False}, error=str(e))

# -------------------------
# Orchestrator
# -------------------------
class Orchestrator:
    def __init__(self):
        self.state = StateStore()
        # circuit breakers for specific external tool groups
        self.doc_cb = CircuitBreaker("doc_service", fail_threshold=4, recovery_timeout=20.0)
        # create agents
        self.retriever = RetrieverAgent("retriever", self.state, cb=self.doc_cb)
        self.enricher = EnricherAgent("enricher", self.state)
        self.planner = PlannerAgent("planner", self.state)
        self.executor = ExecutorAgent("executor", self.state)
        self.notifier = NotifierAgent("notifier", self.state)

    async def run_flow(self, query: str, idempotency_key: Optional[str] = None):
        flow_id = str(uuid.uuid4())[:8]
        METRICS["flows_started"] += 1
        audit("flow_started", {"flow_id": flow_id, "query": query, "idempotency_key": idempotency_key})
        checkpoint_name = f"start_{flow_id}"
        self.state.checkpoint(checkpoint_name)

        try:
            # 1) Retrieve (with fallback to cache)
            retr_res = await self.retriever.run({"query": query})
            docs = retr_res.data.get("docs", [])
            source = retr_res.data.get("source", "unknown")
            logging.info("[Orchestrator] retrieved %d docs (source=%s)", len(docs), source)

            # 2) Enrich (LLM summarization) - has fallback naive summary
            enr_res = await self.enricher.run({"docs": docs})
            summary = enr_res.data.get("summary", "")
            logging.info("[Orchestrator] summary length=%d", len(summary))

            # 3) Plan
            plan_res = await self.planner.run({"summary": summary})
            plan = plan_res.data.get("plan", {})
            logging.info("[Orchestrator] plan=%s", plan)

            # 4) Execute (safety checks inside) - provide idempotency
            exec_res = await self.executor.run({"plan": plan, "idempotency_key": idempotency_key})
            if not exec_res.ok:
                logging.warning("[Orchestrator] execution had issues; will attempt fallback notification")
                # fallback strategy: do not attempt risky retries; notify ops for manual action
                audit("execution_fallback", {"plan": plan, "error": exec_res.error})
                # fallback: set manual review flag
                self.state.set("manual_review", {"flow_id": flow_id, "plan": plan, "error": exec_res.error})
            execution_result = exec_res.data.get("result")

            # 5) Notify final result (best-effort)
            notify_res = await self.notifier.run({"summary": summary, "execution_result": execution_result})
            if not notify_res.ok:
                logging.warning("[Orchestrator] notifier fallback engaged; notification queued for human retry")
            # success
            METRICS["flows_succeeded"] += 1
            audit("flow_completed", {"flow_id": flow_id, "execution_result": execution_result})
            return {"flow_id": flow_id, "status": "completed", "execution": execution_result}
        except Exception as e:
            METRICS["flows_failed"] += 1
            logging.exception("[Orchestrator] unhandled exception in flow %s: %s", flow_id, e)
            audit("flow_failed", {"flow_id": flow_id, "error": str(e)})
            # rollback to safe checkpoint
            self.state.rollback(checkpoint_name)
            # fallback: create manual ticket for human-in-loop
            self.state.set("manual_ticket", {"flow_id": flow_id, "error": str(e)})
            return {"flow_id": flow_id, "status": "failed", "reason": str(e)}

# -------------------------
# Demo runner with scenarios
# -------------------------
async def main_demo():
    orch = Orchestrator()

    queries = [
        "Check for fraud alerts in payments today",
        "Summarize market signals for AAPL and TSLA",
        "Detect suspicious KYC activity in recent onboarding",
    ]

    # run flows serially and then parallel to demonstrate concurrency + isolation
    print("\n--- Running serial flows ---")
    for q in queries:
        res = await orch.run_flow(q, idempotency_key=str(uuid.uuid4()))
        print("Flow result:", res)

    print("\n--- Running parallel flows (concurrency demo) ---")
    parallel_inputs = [
        {"q": "Parallel: evaluate BTC volatility", "idkey": "idp-1"},
        {"q": "Parallel: check AML anomalies", "idkey": "idp-2"},
        {"q": "Parallel: analyze trading signal", "idkey": "idp-3"},
    ]
    tasks = [orch.run_flow(item["q"], idempotency_key=item["idkey"]) for item in parallel_inputs]
    all_results = await asyncio.gather(*tasks)
    for r in all_results:
        print("Parallel flow result:", r)

    print("\n--- Metrics & Audit Summary ---")
    print("METRICS:", METRICS)
    print("AUDIT sample (last 6 entries):")
    for entry in AUDIT_LOG[-6:]:
        print(entry)

if __name__ == "__main__":
    asyncio.run(main_demo())


"""
Multi-Agent Orchestration (pure Python, no frameworks)
- Demonstrates:
  * Orchestrator/Dispatcher
  * Multiple Agents (Retriever, Analyzer, Trader, Notifier)
  * Tools as functions (mock APIs)
  * State management (in-memory store + checkpoints)
  * Branching logic and safety checks
  * Parallel execution using asyncio
  * Retries and simple monitoring/logging
Run: python multi_agent_orchestration.py
"""

import asyncio
import random
import time
import uuid
import logging
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# -----------------------
# Tools (pure functions)
# -----------------------
async def mock_fetch_price(symbol: str) -> Dict[str, Any]:
    """Simulate an async API call that returns a price and metadata."""
    await asyncio.sleep(random.uniform(0.2, 0.8))  # IO delay
    # simulate intermittent failures
    if random.random() < 0.08:
        raise ConnectionError("failed to reach price API")
    price = round(random.uniform(50, 1500), 2)
    return {"symbol": symbol, "price": price, "timestamp": time.time()}


async def mock_place_order(action: str, symbol: str, qty: int, price: float) -> Dict[str, Any]:
    """Simulate placing an order through an exchange API."""
    await asyncio.sleep(random.uniform(0.2, 0.6))
    if random.random() < 0.05:
        raise RuntimeError("order failed: API error")
    order_id = str(uuid.uuid4())
    return {"order_id": order_id, "symbol": symbol, "action": action, "qty": qty, "price": price, "status": "filled"}


async def mock_send_notification(message: str) -> None:
    """Simulate sending notification (email/slack)."""
    await asyncio.sleep(0.1)
    logging.info("[Notifier] %s", message)


# Retry wrapper for tools
async def retry(coro_func, *args, retries=3, backoff=0.3, **kwargs):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            wait = backoff * attempt
            logging.warning("Retry %d/%d for %s failed: %s (sleep %.2fs)", attempt, retries, coro_func.__name__, e, wait)
            await asyncio.sleep(wait)
    raise last_exc


# -----------------------
# State / Memory Store
# -----------------------
class StateStore:
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.checkpoints: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any):
        self.store[key] = value

    def get(self, key: str, default=None):
        return self.store.get(key, default)

    def checkpoint(self, name: str):
        # shallow copy for demo - in production serialize properly
        self.checkpoints[name] = dict(self.store)
        logging.info("[State] Checkpoint created: %s", name)

    def rollback(self, name: str):
        if name in self.checkpoints:
            self.store = dict(self.checkpoints[name])
            logging.info("[State] Rolled back to checkpoint: %s", name)
        else:
            logging.warning("[State] No such checkpoint to rollback: %s", name)


# -----------------------
# Agent base class
# -----------------------
class Agent:
    def __init__(self, name: str, state: StateStore):
        self.name = name
        self.state = state

    async def handle(self, payload: Dict[str, Any]) -> Any:
        raise NotImplementedError


# -----------------------
# Specific Agents
# -----------------------
class RetrieverAgent(Agent):
    """Fetches live prices in parallel using the price tool"""

    async def handle(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        symbols = payload.get("symbols", [])
        logging.info("[%s] Fetching prices for %s", self.name, symbols)

        async def fetch_one(sym):
            # use retry wrapper
            return await retry(mock_fetch_price, sym, retries=3)

        tasks = [fetch_one(s) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        prices = []
        for r in results:
            if isinstance(r, Exception):
                logging.error("[%s] Error fetching price: %s", self.name, r)
            else:
                prices.append(r)
        self.state.set("latest_prices", prices)
        return prices


class AnalyzerAgent(Agent):
    """Analyzes price data and decides: buy / hold / sell for each symbol"""

    async def handle(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        prices = payload.get("prices") or self.state.get("latest_prices", [])
        logging.info("[%s] Analyzing %d price points", self.name, len(prices))
        decisions = []
        for p in prices:
            # very simple heuristic for demo:
            price = p["price"]
            # random noise + thresholding to produce decisions
            score = (random.random() * 2) + (1000 - price) / 1000
            if score > 1.7:
                decision = "buy"
            elif score < 0.6:
                decision = "sell"
            else:
                decision = "hold"
            decisions.append({"symbol": p["symbol"], "price": price, "decision": decision, "reason_score": round(score, 3)})
        self.state.set("decisions", decisions)
        return decisions


class TraderAgent(Agent):
    """Executes trades if safety checks pass"""

    def __init__(self, name: str, state: StateStore, account_balance: float = 100000.0):
        super().__init__(name, state)
        self.balance = account_balance
        self.position = {}  # symbol -> qty

    async def handle(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        decisions = payload.get("decisions") or self.state.get("decisions", [])
        logging.info("[%s] Evaluating %d decisions", self.name, len(decisions))
        execution_results = []

        for d in decisions:
            symbol = d["symbol"]
            decision = d["decision"]
            price = d["price"]

            if decision == "buy":
                qty = int(min(10, max(1, self.balance // (price * 1.1))))  # small position
                cost = qty * price
                # Safety check
                if qty <= 0 or cost > self.balance * 0.2:
                    logging.warning("[%s] Safety blocked buy for %s (qty=%s cost=%.2f balance=%.2f)", self.name, symbol, qty, cost, self.balance)
                    execution_results.append({"symbol": symbol, "action": "blocked", "reason": "safety_check"})
                    continue
                # Place order with retry
                try:
                    result = await retry(mock_place_order, "buy", symbol, qty, price, retries=2)
                    self.balance -= cost
                    self.position[symbol] = self.position.get(symbol, 0) + qty
                    execution_results.append({**result})
                    logging.info("[%s] Bought %s qty=%s price=%.2f", self.name, symbol, qty, price)
                except Exception as e:
                    logging.error("[%s] Order failed for %s: %s", self.name, symbol, e)
                    execution_results.append({"symbol": symbol, "action": "failed", "error": str(e)})
            elif decision == "sell":
                qty = self.position.get(symbol, 0)
                if qty <= 0:
                    logging.info("[%s] No position to sell for %s", self.name, symbol)
                    execution_results.append({"symbol": symbol, "action": "no_pos"})
                    continue
                try:
                    result = await retry(mock_place_order, "sell", symbol, qty, price, retries=2)
                    proceeds = qty * price
                    self.balance += proceeds
                    self.position[symbol] = 0
                    execution_results.append({**result})
                    logging.info("[%s] Sold %s qty=%s price=%.2f", self.name, symbol, qty, price)
                except Exception as e:
                    logging.error("[%s] Sell failed for %s: %s", self.name, symbol, e)
                    execution_results.append({"symbol": symbol, "action": "failed", "error": str(e)})
            else:
                execution_results.append({"symbol": symbol, "action": "hold"})
        # store account snapshot
        self.state.set("trader_snapshot", {"balance": self.balance, "positions": dict(self.position)})
        return execution_results


class NotifierAgent(Agent):
    """Sends notifications based on decisions or orders"""

    async def handle(self, payload: Dict[str, Any]) -> None:
        summary = payload.get("summary") or "No summary"
        await mock_send_notification(summary)
        # also store last notification for audit
        self.state.set("last_notification", {"summary": summary, "time": time.time()})


# -----------------------
# Orchestrator / Dispatcher
# -----------------------
class Orchestrator:
    def __init__(self):
        self.state = StateStore()
        # register agents
        self.retriever = RetrieverAgent("Retriever", self.state)
        self.analyzer = AnalyzerAgent("Analyzer", self.state)
        # Trader gets initial balance from state if present
        self.trader = TraderAgent("Trader", self.state, account_balance=100000.0)
        self.notifier = NotifierAgent("Notifier", self.state)

    async def run_trading_flow(self, symbols: List[str]):
        """
        Orchestrates a trading flow:
         1) checkpoint
         2) parallel fetch prices
         3) analyze decisions
         4) branching: if any 'buy' or 'sell' -> execute trades
         5) notify user
        """
        run_id = str(uuid.uuid4())[:8]
        logging.info("[Orchestrator] Starting trading flow %s for %s", run_id, symbols)
        self.state.checkpoint(f"start_{run_id}")

        try:
            # Step 1: fetch prices in parallel
            prices = await self.retriever.handle({"symbols": symbols})
            if not prices:
                logging.warning("[Orchestrator] No prices fetched; aborting flow")
                await self.notifier.handle({"summary": "No prices available. Flow aborted."})
                return

            # Step 2: analyze
            decisions = await self.analyzer.handle({"prices": prices})

            # Step 3: branching -> decide to trade if any buy/sell
            actionable = [d for d in decisions if d["decision"] in ("buy", "sell")]
            logging.info("[Orchestrator] Decisions: %s", decisions)

            if actionable:
                # For demo: run trading agent
                trade_results = await self.trader.handle({"decisions": decisions})
                # Save trade results to state
                self.state.set("last_trade_results", trade_results)
                # Notify with summary (build a concise message)
                buys = [r for r in trade_results if r.get("action") == "filled" or r.get("status") == "filled"]
                summary = f"Executed {len(buys)} trades. Snapshot: {self.state.get('trader_snapshot')}"
                await self.notifier.handle({"summary": summary})
            else:
                # No action required
                summary = "No trading actions required (all holds)."
                await self.notifier.handle({"summary": summary})

            # Final checkpoint success
            self.state.checkpoint(f"end_{run_id}")
            logging.info("[Orchestrator] Flow %s completed successfully", run_id)
        except Exception as e:
            logging.exception("[Orchestrator] Flow %s failed: %s", run_id, e)
            # rollback to checkpoint
            self.state.rollback(f"start_{run_id}")
            await self.notifier.handle({"summary": f"Flow failed, rolled back. Error: {e}"})

    async def run_parallel_jobs(self, job_requests: List[Dict[str, Any]]):
        """Example of orchestrator running multiple flows in parallel"""
        tasks = []
        for req in job_requests:
            symbols = req.get("symbols", [])
            tasks.append(self.run_trading_flow(symbols))
        await asyncio.gather(*tasks)


# -----------------------
# Demo / Main
# -----------------------
async def main_demo():
    orch = Orchestrator()

    # Example 1: single flow
    await orch.run_trading_flow(["AAPL", "TSLA", "GOOGL"])

    # Example 2: run two flows in parallel (demonstrates concurrency & isolated checkpoints)
    await orch.run_parallel_jobs([
        {"symbols": ["NFLX", "AMZN"]},
        {"symbols": ["BTC", "ETH", "SOL"]},
    ])

    # Print final state for inspection
    logging.info("Final State Store: %s", orch.state.store)


if __name__ == "__main__":
    # run demo
    asyncio.run(main_demo())


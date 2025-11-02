
"""
semantic_kernel_style_demo.py
- KernelFunction decorator to register functions (tools)
- Planner that composes registered functions into a workflow
- Memory store for storing facts and checkpoints
- Demonstrates fallback when a tool fails
"""

from functools import wraps
import time
import random

# ----------------------------
# Tiny kernel & registry
# ----------------------------
KERNEL_REGISTRY = {}

def kernel_function(name=None, description=None):
    def decorator(fn):
        key = name or fn.__name__
        KERNEL_REGISTRY[key] = {"fn": fn, "description": description}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ----------------------------
# Memory store
# ----------------------------
class Memory:
    def __init__(self):
        self.data = {}

    def save(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

# ----------------------------
# Kernel functions (tools)
# ----------------------------
@kernel_function(name="fetch_documents", description="Fetch topical documents")
def fetch_documents(ctx):
    q = ctx.get("query")
    time.sleep(0.2)
    return {"docs": [f"[SK] {q} doc 1", f"[SK] {q} doc 2"]}

@kernel_function(name="summarize_text", description="Create a short summary")
def summarize_text(ctx):
    docs = ctx.get("docs", [])
    time.sleep(0.2)
    # random failure to demonstrate fallback
    if random.random() < 0.15:
        raise RuntimeError("summarizer crashed")
    return {"summary": " ".join(d[:120] for d in docs)[:200] + "..."}

@kernel_function(name="format_reply", description="Format the final reply")
def format_reply(ctx):
    summary = ctx.get("summary", "No summary")
    return {"reply": f"SemanticKernelReply: {summary}"}

# ----------------------------
# Planner / Orchestrator
# ----------------------------
class SKPlanner:
    def __init__(self, memory: Memory):
        self.memory = memory

    def compose(self, user_query):
        # Compose a list of kernel function keys to call
        plan = ["fetch_documents", "summarize_text", "format_reply"]
        self.memory.save("last_query", user_query)
        return plan

    def run(self, plan, initial_ctx):
        ctx = dict(initial_ctx)  # working context
        for step in plan:
            tool_meta = KERNEL_REGISTRY.get(step)
            if not tool_meta:
                raise KeyError(f"Tool {step} not registered in kernel.")
            fn = tool_meta["fn"]
            try:
                out = fn(ctx)  # synchronous call
                if isinstance(out, dict):
                    ctx.update(out)
                print(f"[SK] Step '{step}' OK")
            except Exception as e:
                print(f"[SK] Step '{step}' failed: {e}")
                # Fallback strategy: attempt a simple fallback or skip
                fallback_out = self.fallback(step, ctx, e)
                ctx.update(fallback_out)
        return ctx

    def fallback(self, step, ctx, error):
        # Example fallback: if summarizer fails, create a naive summary
        if step == "summarize_text":
            docs = ctx.get("docs", [])
            naive = " ".join(docs)[:150] + "..."
            print("[SK] Using fallback naive summarizer")
            return {"summary": naive}
        # default: return empty modification
        return {}

# ----------------------------
# Demo usage
# ----------------------------
def demo_semantic_kernel_style(query):
    print("\n--- Semantic Kernel-style Planner Demo ---")
    mem = Memory()
    planner = SKPlanner(mem)
    plan = planner.compose(query)
    final_ctx = planner.run(plan, {"query": query})
    print("\nFinal context:", final_ctx)
    print("Memory:", mem.data)

if __name__ == "__main__":
    demo_semantic_kernel_style("KYC requirements for banks in India")

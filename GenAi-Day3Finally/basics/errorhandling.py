
import random
import time

# -------------------------------
# Primary "Agent" - Main Service
# -------------------------------
def primary_agent(task):
    """Simulate a main AI agent that might fail randomly."""
    print(f"[Primary Agent] Processing: {task}")
    time.sleep(1)
    if random.choice([True, False]):  # Random failure simulation
        raise ValueError("Primary agent failed to complete the task.")
    return f"✅ Primary Agent successfully handled: {task}"

# -------------------------------
# Fallback "Agent" - Backup Plan
# -------------------------------
def fallback_agent(task):
    """Fallback agent used when primary fails."""
    print(f"[Fallback Agent] Taking over: {task}")
    time.sleep(0.5)
    return f"⚙️ Fallback Agent handled task safely: {task}"

# -------------------------------
# Error Handling and Orchestration
# -------------------------------
def orchestrate_task(task):
    """Orchestrator manages error handling and fallback."""
    try:
        result = primary_agent(task)
    except Exception as e:
        print(f"[Error] {e}")
        print("[System] Switching to fallback agent...")
        result = fallback_agent(task)
    finally:
        print("[System] Task pipeline completed.\n")
    return result

# -------------------------------
# Test the mechanism
# -------------------------------
if __name__ == "__main__":
    tasks = ["Generate Report", "Fetch Market Data", "Analyze Sentiment", "Summarize Emails"]
    for t in tasks:
        output = orchestrate_task(t)
        print("Result:", output)

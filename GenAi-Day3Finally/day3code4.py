import logging
import datetime
import re

# -----------------------------
# Setup Logging (Auditable)
# -----------------------------
logging.basicConfig(
    filename='ai_agent_audit.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# -----------------------------
# Safe Prompt Handling
# -----------------------------
ALLOWED_COMMANDS = ["get_metrics", "forecast_demand", "fetch_docs", "safety_check"]

def sanitize_user_input(user_query: str) -> str:
    """Strip unsafe characters and enforce allowed commands."""
    user_query = user_query.strip()
    # Only allow known command words
    if not any(cmd in user_query for cmd in ALLOWED_COMMANDS):
        raise ValueError("Command not allowed for safety reasons.")
    # Remove suspicious characters
    user_query = re.sub(r"[;&|`$<>]", "", user_query)
    return user_query

# -----------------------------
# AI Agent Simulation
# -----------------------------
def ai_agent(user_query: str) -> dict:
    """
    Process user query safely, log actions, and return structured response.
    """
    try:
        # 1. Sanitize input
        safe_query = sanitize_user_input(user_query)
        logging.info(f"Received query: {safe_query}")

        # 2. Decide action (simulate)
        if "get_metrics" in safe_query:
            result = {"region": "north", "frequency_hz": 49.98, "status": "NORMAL"}
        elif "forecast_demand" in safe_query:
            result = {"region": "north", "next_24h_load": [950, 960, 970]}
        elif "fetch_docs" in safe_query:
            result = {"topic": "grid maintenance", "content": "Runbook for grid fault handling."}
        elif "safety_check" in safe_query:
            result = {"allowed": True, "reason": "All safe"}
        else:
            result = {"error": "Unknown or unsafe command"}

        # 3. Log the action and result
        logging.info(f"Action result: {result}")

        return {"status": "success", "result": result}

    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {"status": "error", "message": str(e)}

# -----------------------------
# Demo Usage
# -----------------------------
if __name__ == "__main__":
    queries = [
        "get_metrics for north",
        "forecast_demand next 24h",
        "fetch_docs grid maintenance",
        "safety_check north zone",
        "rm -rf /"  # Unsafe query test
    ]

    for q in queries:
        response = ai_agent(q)
        print(f"Query: {q}\nResponse: {response}\n{'-'*50}")


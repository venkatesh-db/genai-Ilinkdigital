

import json
import time
import random

# --------------------------
# STEP 1. Smart Grid Agent Core
# --------------------------
MAX_STEPS = 5


def smart_grid_agent(user_query):
    """
    Smart Grid Assistant Agent with context-sensitive decision flow.
    """

    context = []
    step = 0
    last_action = None

    while step < MAX_STEPS:
        step += 1

        llm_output = generate_llm_output(user_query, context)

        try:
            parsed = json.loads(llm_output)
            action = parsed.get("action")
            inp = parsed.get("input", {})
        except Exception as e:
            return {"error": f"Invalid LLM output: {e}", "raw_output": llm_output}

        # Prevent infinite repetition
        if action == last_action and step > 1:
            return {
                "error": "stuck_loop_detected",
                "last_action": last_action,
                "context": context
            }

        last_action = action

        # --- Action dispatch ---
        if action == "get_grid_metrics":
            result = simulate_get_grid_metrics(inp)
        elif action == "forecast_demand":
            result = simulate_forecast_demand(inp)
        elif action == "create_incident_ticket":
            result = simulate_create_ticket(inp)
        elif action == "control_device":
            result = simulate_control(inp)
        elif action == "fetch_docs":
            result = simulate_fetch_docs(inp)
        elif action == "safety_check":
            result = simulate_safety_check(inp)
        else:
            return {"error": f"Unknown action: {action}", "raw": llm_output}

        context.append(f"TOOL_RESULT -> {action}: {json.dumps(result)}")

        # Exit condition
        if action in ["forecast_demand", "create_incident_ticket", "fetch_docs"]:
            return {
                "status": "success",
                "context": context,
                "final_action": action,
                "result": result
            }

    return {"error": "max_steps_exceeded", "context": context}


# --------------------------
# STEP 2. Mock "LLM" Output Generator
# --------------------------
def generate_llm_output(user_query, context):
    """
    Simulated reasoning step — returns a JSON decision for the agent.
    """

    user_query = user_query.lower()

    if "metric" in user_query or "status" in user_query:
        return json.dumps({
            "action": "get_grid_metrics",
            "input": {"region": "north"}
        })
    elif "forecast" in user_query or "predict" in user_query:
        return json.dumps({
            "action": "forecast_demand",
            "input": {"region": "north", "horizon_hours": 24}
        })
    elif "alarm" in user_query or "incident" in user_query:
        return json.dumps({
            "action": "create_incident_ticket",
            "input": {"summary": "Grid alarm triggered", "severity": "high"}
        })
    elif "safety" in user_query:
        return json.dumps({
            "action": "safety_check",
            "input": {"region": "north"}
        })
    elif "control" in user_query or "switch" in user_query:
        return json.dumps({
            "action": "control_device",
            "input": {"device_id": "TR-1023", "action": "shutdown"}
        })
    elif "manual" in user_query or "docs" in user_query:
        return json.dumps({
            "action": "fetch_docs",
            "input": {"topic": "grid maintenance"}
        })

    # Default fallback
    return json.dumps({
        "action": "get_grid_metrics",
        "input": {"region": "north"}
    })


# --------------------------
# STEP 3. Tool Simulators
# --------------------------
def simulate_get_grid_metrics(inp):
    region = inp.get("region", "unknown")
    return {
        "region": region,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "frequency_hz": 49.98,
        "voltage_pu": 0.985,
        "total_load_mw": random.uniform(1000, 1500),
        "renewable_share_pct": round(random.uniform(30, 45), 2),
        "alarms": ["line_trip"] if region == "north" else []
    }


def simulate_forecast_demand(inp):
    region = inp.get("region")
    horizon = inp.get("horizon_hours", 24)
    return {
        "region": region,
        "horizon_hours": horizon,
        "predicted_load_mw": [round(1200 + i * 3 + random.uniform(-10, 10), 2) for i in range(horizon)]
    }


def simulate_create_ticket(inp):
    return {
        "ticket_id": f"INC-{int(time.time())}",
        "summary": inp.get("summary"),
        "severity": inp.get("severity"),
        "status": "created"
    }


def simulate_control(inp):
    return {"device_id": inp.get("device_id"), "action": inp.get("action"), "status": "ok"}


def simulate_fetch_docs(inp):
    return {"topic": inp.get("topic"), "content": "Runbook for grid fault handling."}


def simulate_safety_check(inp):
    return {"allowed": True, "reason": "All parameters within safety limits."}


# --------------------------
# STEP 4. Run Demo
# --------------------------
if __name__ == "__main__":
    print("\n=== ⚡ Smart Grid Assistant Demo ===\n")

    queries = [
        "Give me the latest metrics for the north region and tell me if any alarms need action.",
        "Forecast demand for next 24 hours in north region.",
        "Check safety for north zone devices.",
        "Create an incident ticket for grid fault in east region.",
        "Fetch grid manual documents."
    ]

    for q in queries:
        print(f"\n🧠 USER QUERY: {q}")
        result = smart_grid_agent(q)
        print(json.dumps(result, indent=2))
        print("-" * 60)

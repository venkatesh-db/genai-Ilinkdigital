
import json
import time
import random

MAX_STEPS = 5

def smart_grid_agent(user_query):
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

        if action == last_action and step > 1:
            return {
                "status": "done",
                "note": "No further action required.",
                "context": context
            }

        last_action = action

        # Dispatch actions
        if action == "get_grid_metrics":
            result = simulate_get_grid_metrics(inp)
            context.append(f"TOOL_RESULT -> get_grid_metrics: {json.dumps(result)}")

            # Auto-handle alarms
            if result["alarms"]:
                user_query = "create incident ticket for alarm"
                continue

        elif action == "safety_check":
            result = simulate_safety_check(inp)
            context.append(f"TOOL_RESULT -> safety_check: {json.dumps(result)}")

            # Auto-ticket unsafe
            if not result["allowed"]:
                user_query = "create incident ticket for safety issue"
                continue

        elif action == "forecast_demand":
            result = simulate_forecast_demand(inp)
            context.append(f"TOOL_RESULT -> forecast_demand: {json.dumps(result)}")
            return {"status": "success", "final_action": "forecast_demand", "result": result}

        elif action == "create_incident_ticket":
            result = simulate_create_ticket(inp)
            context.append(f"TOOL_RESULT -> create_incident_ticket: {json.dumps(result)}")
            return {"status": "success", "final_action": "create_incident_ticket", "result": result}

        elif action == "fetch_docs":
            result = simulate_fetch_docs(inp)
            context.append(f"TOOL_RESULT -> fetch_docs: {json.dumps(result)}")
            return {"status": "success", "final_action": "fetch_docs", "result": result}

        elif action == "control_device":
            result = simulate_control(inp)
            context.append(f"TOOL_RESULT -> control_device: {json.dumps(result)}")
            return {"status": "success", "final_action": "control_device", "result": result}

        else:
            return {"error": f"Unknown action: {action}", "context": context}

    return {"error": "max_steps_exceeded", "context": context}


# --------------------------
# Simulated LLM Decision Engine
# --------------------------
def generate_llm_output(user_query, context):
    user_query = user_query.lower()

    if "metric" in user_query or "status" in user_query:
        return json.dumps({"action": "get_grid_metrics", "input": {"region": "north"}})
    elif "forecast" in user_query:
        return json.dumps({"action": "forecast_demand", "input": {"region": "north", "horizon_hours": 24}})
    elif "incident" in user_query or "alarm" in user_query:
        return json.dumps({"action": "create_incident_ticket", "input": {"summary": "Grid alarm triggered", "severity": "high"}})
    elif "safety" in user_query:
        return json.dumps({"action": "safety_check", "input": {"region": "north"}})
    elif "control" in user_query:
        return json.dumps({"action": "control_device", "input": {"device_id": "TR-1023", "action": "shutdown"}})
    elif "manual" in user_query or "docs" in user_query:
        return json.dumps({"action": "fetch_docs", "input": {"topic": "grid maintenance"}})

    return json.dumps({"action": "get_grid_metrics", "input": {"region": "north"}})


# --------------------------
# Tool Simulators
# --------------------------
def simulate_get_grid_metrics(inp):
    region = inp.get("region", "unknown")
    alarms = ["line_trip"] if random.random() < 0.4 else []  # 40% chance of alarm
    return {
        "region": region,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "frequency_hz": round(random.uniform(49.9, 50.1), 3),
        "voltage_pu": round(random.uniform(0.97, 1.03), 3),
        "total_load_mw": round(random.uniform(1000, 1500), 2),
        "renewable_share_pct": round(random.uniform(30, 45), 2),
        "alarms": alarms
    }


def simulate_forecast_demand(inp):
    region = inp.get("region")
    horizon = inp.get("horizon_hours", 24)
    forecast = [round(1200 + i * 3 + random.uniform(-15, 15), 2) for i in range(horizon)]
    return {"region": region, "horizon_hours": horizon, "predicted_load_mw": forecast}


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
    allowed = random.random() > 0.2
    return {"allowed": allowed, "reason": "All safe" if allowed else "High current detected."}


# --------------------------
# Demo
# --------------------------
if __name__ == "__main__":
    print("\n=== ⚡ Smart Grid Assistant (Improved Version) ===\n")

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

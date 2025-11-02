
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from typing import TypedDict, Annotated
import random
import os

# ============ TOOLS SIMULATING REAL EMS SYSTEM ============

@tool
def read_solar_meter(_) -> str:
    """Read solar energy meter."""
    return f"Solar Power: {round(random.uniform(80, 120), 2)} kWh"

@tool
def read_hvac_meter(_) -> str:
    """Read HVAC energy meter."""
    return f"HVAC Power: {round(random.uniform(30, 60), 2)} kWh"

@tool
def read_lighting_meter(_) -> str:
    """Read lighting energy meter."""
    return f"Lighting Power: {round(random.uniform(10, 25), 2)} kWh"

@tool
def alert_supervisor(data: str) -> str:
    """Send alert to energy supervisor."""
    return f"⚠️ Alert sent to supervisor: {data}"

@tool
def optimize_usage(data: str) -> str:
    """Suggest energy optimization based on usage."""
    return f"💡 Suggestion: Reduce HVAC load by 10% and enable smart lighting schedule. Data={data}"

# ============ STATE DEFINITION ============

class EMSState(TypedDict):
    readings: dict
    total_usage: float
    path_taken: str

# ============ BUILD LANGGRAPH FLOW ============

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  No OpenAI API key found. Running in demo mode...")
    DEMO_MODE = True
else:
    DEMO_MODE = False
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

graph = StateGraph(EMSState)

# Step 1: Parallel sensors (branch)
def get_readings(state: EMSState):
    """Collect parallel readings from solar, HVAC, and lighting meters."""
    # Direct function calls instead of tool invocation
    solar_reading = f"Solar Power: {round(random.uniform(80, 120), 2)} kWh"
    hvac_reading = f"HVAC Power: {round(random.uniform(30, 60), 2)} kWh"
    lighting_reading = f"Lighting Power: {round(random.uniform(10, 25), 2)} kWh"
    
    readings = {
        "solar": solar_reading,
        "hvac": hvac_reading,
        "lighting": lighting_reading
    }
    print(f"📊 Readings collected:")
    for system, reading in readings.items():
        print(f"  • {system.upper()}: {reading}")
    
    return {"readings": readings}

graph.add_node("get_readings", get_readings)

# Step 2: Check conditions and branch
def analyze_usage(state: EMSState):
    readings = state["readings"]
    
    # Extract numerical values from readings
    solar_val = float(readings["solar"].split(": ")[1].split(" ")[0])
    hvac_val = float(readings["hvac"].split(": ")[1].split(" ")[0])
    lighting_val = float(readings["lighting"].split(": ")[1].split(" ")[0])
    
    total = solar_val + hvac_val + lighting_val
    print(f"\n🔍 Analysis: Total Power Usage: {total:.2f} kWh")

    if total > 160:
        print("⚠️  High usage detected - routing to alert path")
        return "alert_path"
    else:
        print("✅ Normal usage - routing to optimization path")
        return "optimize_path"

graph.add_conditional_edges(
    "get_readings",
    analyze_usage,
    {
        "alert_path": "alert_supervisor",
        "optimize_path": "optimize_usage"
    }
)

# Step 3a: Alert node
def alert_node(state: EMSState):
    result = "⚠️ Alert sent to supervisor: High energy usage detected!"
    print(f"🚨 Alert: {result}")
    return {"path_taken": "alert"}

graph.add_node("alert_supervisor", alert_node)

# Step 3b: Optimization node
def optimize_node(state: EMSState):
    result = "💡 Suggestion: Reduce HVAC load by 10% and enable smart lighting schedule."
    print(f"⚡ Optimization: {result}")
    return {"path_taken": "optimize"}

graph.add_node("optimize_usage", optimize_node)

# Step 4: End
graph.add_edge("alert_supervisor", END)
graph.add_edge("optimize_usage", END)

# ============ EXECUTION ============

# Set entry point and compile
graph.set_entry_point("get_readings")
app = graph.compile()

if __name__ == "__main__":
    print("⚙️  LangGraph EMS Workflow - Energy Management System")
    print("=" * 55)
    
    # Initialize state
    initial_state = {
        "readings": {},
        "total_usage": 0.0,
        "path_taken": ""
    }
    
    try:
        result = app.invoke(initial_state)
        print(f"\n✅ Workflow Complete!")
        print(f"📋 Final State:")
        print(f"  • Readings: {result.get('readings', {})}")
        print(f"  • Path taken: {result.get('path_taken', 'unknown')}")
        
    except Exception as e:
        print(f"\n❌ Workflow Error: {e}")
        print("Running in demo mode...")
        
        # Demo simulation
        print("\n🔄 Demo simulation:")
        solar = round(random.uniform(80, 120), 2)
        hvac = round(random.uniform(30, 60), 2)
        lighting = round(random.uniform(10, 25), 2)
        total = solar + hvac + lighting
        
        print(f"📊 Simulated readings:")
        print(f"  • Solar: {solar} kWh")
        print(f"  • HVAC: {hvac} kWh") 
        print(f"  • Lighting: {lighting} kWh")
        print(f"🔍 Total: {total:.2f} kWh")
        
        if total > 160:
            print("🚨 HIGH USAGE ALERT - Supervisor notified")
        else:
            print("⚡ Normal usage - Optimization suggestions generated")

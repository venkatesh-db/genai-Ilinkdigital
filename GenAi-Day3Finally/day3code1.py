import asyncio
import random
from enum import Enum
from typing import Dict

# ==============================
# ENUMS AND SHARED STATE
# ==============================

class GridState(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

shared_state = {
    "energy_demand": 1000,  # MW
    "energy_supply": 1000,  # MW
    "carbon_emission": 50.0,  # ppm
    "state": GridState.NORMAL,
}

# ==============================
# BASE CLASS FOR AI AGENTS
# ==============================

class SmartAgent:
    def __init__(self, name: str):
        self.name = name

    async def act(self, state: Dict):
        raise NotImplementedError

    def log(self, message: str):
        print(f"[{self.name}] {message}")

# ==============================
# ENERGY BALANCER AGENT
# ==============================

class EnergyBalancer(SmartAgent):
    async def act(self, state: Dict):
        demand = state["energy_demand"]
        supply = state["energy_supply"]

        # Adjust generation if imbalance detected
        if supply < demand:
            diff = demand - supply
            state["energy_supply"] += diff * 0.5
            self.log(f"Increasing supply by {diff * 0.5:.1f} MW to match demand")
        elif supply > demand:
            diff = supply - demand
            state["energy_supply"] -= diff * 0.3
            self.log(f"Reducing supply by {diff * 0.3:.1f} MW to optimize cost")

# ==============================
# EMISSION CONTROLLER AGENT
# ==============================

class EmissionController(SmartAgent):
    async def act(self, state: Dict):
        emission = state["carbon_emission"]
        if emission > 70:
            state["state"] = GridState.CRITICAL
            state["carbon_emission"] -= 10
            self.log(f"⚠️ Emission critical: {emission:.2f} → taking control measures!")
        elif emission > 55:
            state["state"] = GridState.WARNING
            state["carbon_emission"] -= 5
            self.log(f"Warning: High emission {emission:.2f} → reducing!")
        else:
            state["state"] = GridState.NORMAL
            self.log(f"Emission stable at {emission:.2f}")

# ==============================
# DEMAND FORECASTER AGENT
# ==============================

class DemandForecaster(SmartAgent):
    async def act(self, state: Dict):
        change = random.uniform(-50, 50)
        state["energy_demand"] += change
        self.log(f"Forecast demand change: {change:+.1f} MW (new={state['energy_demand']:.1f})")

# ==============================
# ANOMALY DETECTOR AGENT
# ==============================

class AnomalyDetector(SmartAgent):
    async def act(self, state: Dict):
        anomaly_detected = random.random() < 0.1  # 10% chance
        if anomaly_detected:
            self.log("🚨 Anomaly detected in sensor data! Flagging for review.")
            state["state"] = GridState.WARNING

# ==============================
# GRID ORCHESTRATOR
# ==============================

class GridOrchestrator:
    def __init__(self):
        self.agents = [
            DemandForecaster("DemandForecaster"),
            EnergyBalancer("EnergyBalancer"),
            EmissionController("EmissionController"),
            AnomalyDetector("AnomalyDetector"),
        ]
        self.iteration = 0

    async def orchestrate(self):
        global shared_state
        while self.iteration < 10:
            self.iteration += 1
            print(f"\n=== ITERATION {self.iteration} ===")
            shared_state["carbon_emission"] += random.uniform(-5, 5)

            # Run agents in parallel
            await asyncio.gather(*(agent.act(shared_state) for agent in self.agents))

            # Evaluate grid health after all agents run
            self.evaluate_grid(shared_state)
            await asyncio.sleep(1)

        print("\n=== FINAL GRID STATE ===")
        for k, v in shared_state.items():
            print(f"{k}: {v}")

    def evaluate_grid(self, state):
        if state["state"] == GridState.CRITICAL:
            print("[GRID] CRITICAL CONDITION → Emergency protocol activated 🚨")
        elif state["state"] == GridState.WARNING:
            print("[GRID] Warning → Emission or demand imbalance ⚠️")
        else:
            print("[GRID] Stable and efficient ✅")

# ==============================
# MAIN
# ==============================

async def main():
    print("Starting Smart Grid Orchestration Demo ⚡️")
    orchestrator = GridOrchestrator()
    await orchestrator.orchestrate()

if __name__ == "__main__":
    asyncio.run(main())

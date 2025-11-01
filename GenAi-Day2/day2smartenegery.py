
import asyncio
import random
from dataclasses import dataclass, field

# -----------------------------
# State Management
# -----------------------------
@dataclass
class EnergyState:
    solar: float = 0.0
    wind: float = 0.0
    grid: float = 0.0
    total: float = 0.0
    status: str = "OK"
    history: list = field(default_factory=list)

    def update(self):
        self.total = self.solar + self.wind + self.grid
        self.history.append({
            "solar": self.solar,
            "wind": self.wind,
            "grid": self.grid,
            "total": self.total,
            "status": self.status
        })


# -----------------------------
# Async Sensor Fetchers
# -----------------------------
async def fetch_solar_data():
    await asyncio.sleep(random.uniform(0.5, 1.5))
    return random.uniform(2.0, 10.0)  # kWh

async def fetch_wind_data():
    await asyncio.sleep(random.uniform(0.5, 1.5))
    return random.uniform(1.0, 8.0)

async def fetch_grid_data():
    await asyncio.sleep(random.uniform(0.5, 1.5))
    return random.uniform(5.0, 12.0)


# -----------------------------
# Branching Logic
# -----------------------------
def evaluate_energy(state: EnergyState):
    if state.total < 10:
        state.status = "LOW - Activate Backup Generator"
    elif state.total > 25:
        state.status = "HIGH - Store Excess Energy"
    else:
        state.status = "NORMAL"
    state.update()


# -----------------------------
# Parallel Monitoring
# -----------------------------
async def monitor_energy(state: EnergyState):
    print("⚙️ Starting energy monitoring system...\n")

    for cycle in range(5):  # Run 5 monitoring cycles
        solar_task = asyncio.create_task(fetch_solar_data())
        wind_task = asyncio.create_task(fetch_wind_data())
        grid_task = asyncio.create_task(fetch_grid_data())

        # Run all sensors in parallel
        solar, wind, grid = await asyncio.gather(solar_task, wind_task, grid_task)

        # Update state
        state.solar, state.wind, state.grid = solar, wind, grid
        evaluate_energy(state)

        print(f"Cycle {cycle + 1}:")
        print(f"☀️ Solar: {solar:.2f} | 🌬 Wind: {wind:.2f} | ⚡ Grid: {grid:.2f}")
        print(f"Total: {state.total:.2f} kWh → Status: {state.status}\n")

        await asyncio.sleep(1)  # Wait before next cycle

    print("✅ Monitoring complete.")


# -----------------------------
# Main Entry
# -----------------------------
async def main():
    energy_state = EnergyState()
    await monitor_energy(energy_state)

    print("\n📊 Energy History Summary:")
    for entry in energy_state.history:
        print(entry)


if __name__ == "__main__":
    asyncio.run(main())

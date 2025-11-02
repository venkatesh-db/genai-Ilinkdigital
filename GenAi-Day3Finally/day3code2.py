

import asyncio
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Simulated tool functions
async def get_grid_metrics(region):
    if random.random() < 0.1:
        raise RuntimeError(f"Primary metrics source failed for {region}")
    await asyncio.sleep(0.5)
    return {
        "region": region,
        "frequency_hz": round(49.8 + random.random() * 0.4, 2),
        "voltage_pu": round(0.98 + random.random() * 0.03, 3),
        "total_load_mw": round(1000 + random.random() * 500, 2),
        "alarms": [] if random.random() < 0.8 else ["line_trip"]
    }

async def get_grid_metrics_fallback(region):
    # Secondary source or default values
    await asyncio.sleep(0.3)
    logging.warning(f"Using fallback metrics for {region}")
    return {
        "region": region,
        "frequency_hz": 50.0,
        "voltage_pu": 1.0,
        "total_load_mw": 1000,
        "alarms": []
    }

async def forecast_demand(region, hours=24):
    if random.random() < 0.1:
        raise RuntimeError(f"Forecasting failed for {region}")
    await asyncio.sleep(0.4)
    return [round(900 + random.random() * 200, 2) for _ in range(hours)]

async def safety_check(region):
    await asyncio.sleep(0.2)
    return {"allowed": True, "reason": "All parameters within safe limits"}

# Monitoring agent
async def monitor_region(region):
    logging.info(f"Starting monitoring for region: {region}")
    state = {"region": region, "metrics": None, "forecast": None, "safety": None}

    try:
        metrics = await get_grid_metrics(region)
    except Exception as e:
        logging.error(f"Error fetching metrics for {region}: {e}")
        metrics = await get_grid_metrics_fallback(region)
    state["metrics"] = metrics

    try:
        forecast = await forecast_demand(region)
        state["forecast"] = forecast
    except Exception as e:
        logging.error(f"Error forecasting demand for {region}: {e}")
        state["forecast"] = [metrics["total_load_mw"]] * 24  # fallback: flat load

    try:
        safety = await safety_check(region)
        state["safety"] = safety
    except Exception as e:
        logging.error(f"Error in safety check for {region}: {e}")
        state["safety"] = {"allowed": False, "reason": "Safety check failed"}

    # Evaluate alarms
    if metrics["alarms"]:
        logging.warning(f"Region {region} has alarms: {metrics['alarms']}")
    else:
        logging.info(f"Region {region} operating normally.")

    return state

async def main():
    regions = ["north", "south", "east", "west"]

    # Run all regions concurrently
    tasks = [monitor_region(region) for region in regions]
    results = await asyncio.gather(*tasks)

    logging.info("\n=== FINAL STATE SUMMARY ===")
    for state in results:
        logging.info(state)

if __name__ == "__main__":
    asyncio.run(main())

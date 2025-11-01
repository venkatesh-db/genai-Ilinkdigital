#!/usr/bin/env python3
"""
Emission Monitoring Flow with state management, branching, and parallel execution.

Run:
    python emission_monitor.py
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

# --- Configuration ---
REGIONS = ["north", "south", "east", "west"]
SENSOR_PER_REGION = 4

# thresholds (units: e.g., gCO2/m3 or arbitrary pollutant units)
THRESHOLD_WARNING = 70.0
THRESHOLD_CRITICAL = 90.0

AGGREGATION_INTERVAL = 5        # seconds between aggregate checks
FORECAST_INTERVAL = 15         # seconds (mock forecasting frequency)
SENSOR_POLL_INTERVAL = 2       # seconds normal polling
HIGH_FREQ_POLL_INTERVAL = 1    # seconds when elevated

# --- State Management Data Structures ---

@dataclass
class RegionState:
    region: str
    sensors: Dict[str, float] = field(default_factory=dict)
    last_aggregate: float = 0.0
    status: str = "NORMAL"  # NORMAL, ELEVATED, WARNING, CRITICAL, MITIGATING, RESOLVED
    history: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_tasks: List[str] = field(default_factory=list)
    last_update_ts: float = field(default_factory=time.time)


# Global state (in-memory): region -> RegionState
STATE: Dict[str, RegionState] = {}

# Simple ticket store
TICKET_DB: Dict[str, Dict[str, Any]] = {}

# --- Tools / Simulations ---


async def mock_sensor_read(region: str, sensor_id: str) -> float:
    """
    Simulate a sensor read. Emissions vary randomly; regions may have different baselines.
    """
    base = {"north": 50, "south": 40, "east": 60, "west": 45}[region]
    # occasional spikes
    spike = 0.0
    if random.random() < 0.05:
        spike = random.uniform(20, 50)
    value = base + random.uniform(-8, 8) + spike
    await asyncio.sleep(0)  # keep it awaitable
    return round(value, 2)


async def safety_check(region: str, aggregate_value: float) -> Tuple[bool, str]:
    """
    Determine whether mitigation can be performed safely.
    """
    # Mock checks: if aggregate > 150 -> unsafe to do remote mitigation
    if aggregate_value > 150:
        return False, "Aggregate emissions extremely high; require manual intervention"
    return True, "OK"


async def mitigation_action(region: str, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Simulate taking a mitigation action (e.g., reduce load, adjust boiler).
    Runs asynchronously and returns result.
    """
    params = params or {}
    # simulate variable time taken
    await asyncio.sleep(random.uniform(1.0, 2.5))
    success = random.random() > 0.1  # 90% success
    result = {
        "region": region,
        "action": action,
        "params": params,
        "status": "success" if success else "failed",
        "timestamp": time.time(),
    }
    return result


async def create_incident(summary: str, region: str, severity: str = "high") -> Dict[str, Any]:
    ticket_id = f"TKT-{int(time.time()*1000) % 1000000}"
    ticket = {
        "ticket_id": ticket_id,
        "summary": summary,
        "region": region,
        "severity": severity,
        "status": "open",
        "created_at": time.time()
    }
    TICKET_DB[ticket_id] = ticket
    await asyncio.sleep(0)  # simulate async write
    return ticket


async def notify_ops(region: str, message: str) -> None:
    # Simulate sending notification (email/SMS)
    print(f"[NOTIFY] Region={region}: {message}")
    await asyncio.sleep(0)


# --- Core Flow: monitoring, aggregation, branching, mitigations ---


async def sensor_task(region: str, sensor_id: str, stop_event: asyncio.Event):
    """
    Poll a single sensor at the appropriate frequency depending on region status.
    Updates STATE in place.
    """
    while not stop_event.is_set():
        state = STATE[region]
        # adjust poll interval depending on state
        if state.status in ("ELEVATED", "WARNING", "CRITICAL", "MITIGATING"):
            interval = HIGH_FREQ_POLL_INTERVAL
        else:
            interval = SENSOR_POLL_INTERVAL

        value = await mock_sensor_read(region, sensor_id)
        state.sensors[sensor_id] = value
        state.last_update_ts = time.time()
        # push to history a light record
        state.history.append({"ts": time.time(), "sensor": sensor_id, "value": value})
        # limit history size
        if len(state.history) > 200:
            state.history.pop(0)
        await asyncio.wait([stop_event.wait()], timeout=interval)


async def aggregator_task(region: str, stop_event: asyncio.Event):
    """
    Periodically aggregate sensor readings and apply branching logic.
    """
    while not stop_event.is_set():
        await asyncio.wait([stop_event.wait()], timeout=AGGREGATION_INTERVAL)
        state = STATE[region]
        if not state.sensors:
            continue
        # compute simple average
        values = list(state.sensors.values())
        aggregate = sum(values) / len(values)
        aggregate = round(aggregate, 2)
        state.last_aggregate = aggregate
        state.last_update_ts = time.time()

        print(f"[AGGREGATE] {region} avg_emission={aggregate} sensors={len(values)} state={state.status}")

        # Branching logic
        if aggregate >= THRESHOLD_CRITICAL:
            # escalate to critical
            if state.status != "CRITICAL":
                state.status = "CRITICAL"
                await notify_ops(region, f"CRITICAL emissions: {aggregate} >= {THRESHOLD_CRITICAL}")
            # run safety check then mitigation in parallel
            allowed, reason = await safety_check(region, aggregate)
            if not allowed:
                # create ticket and notify ops immediately
                ticket = await create_incident(summary=f"Unsafe to auto-mitigate: {reason}", region=region, severity="critical")
                await notify_ops(region, f"Incident created: {ticket['ticket_id']} due to safety check failure")
                state.history.append({"incident": ticket})
            else:
                # set status and start parallel mitigations
                state.status = "MITIGATING"
                # perform several mitigation actions in parallel (e.g., reduce load, reroute)
                mitigation_coros = [
                    mitigation_action(region, "reduce_boiler_output", {"pct": 10}),
                    mitigation_action(region, "activate_scrubbers", {}),
                    mitigation_action(region, "ramp_down_noncritical_plants", {"pct": 5}),
                ]
                # Run mitigations concurrently and record results
                results = await asyncio.gather(*mitigation_coros, return_exceptions=True)
                state.mitigation_tasks.extend([str(r) for r in results])
                # if at least one succeeded, mark resolved->WARNING or ELEVATED based on aggregate
                succeeded = any(isinstance(r, dict) and r.get("status") == "success" for r in results)
                if succeeded:
                    # small cooldown: re-evaluate aggregate quickly (we'll wait AGGREGATION_INTERVAL next loop)
                    await notify_ops(region, f"Mitigation actions executed for {region}. Re-evaluating.")
                    # create a ticket summarizing mitigation
                    ticket = await create_incident(summary=f"Mitigations executed for high emissions in {region}", region=region, severity="high")
                    state.history.append({"mitigation_ticket": ticket})
                    state.status = "WARNING" if aggregate >= THRESHOLD_WARNING else "ELEVATED"
                else:
                    ticket = await create_incident(summary=f"Mitigation FAILED for {region}", region=region, severity="critical")
                    await notify_ops(region, f"Mitigation failed; incident {ticket['ticket_id']} created")
                    state.history.append({"mitigation_failed_ticket": ticket})
        elif aggregate >= THRESHOLD_WARNING:
            # warning path
            if state.status not in ("WARNING", "MITIGATING"):
                state.status = "WARNING"
                await notify_ops(region, f"WARNING emissions: {aggregate} >= {THRESHOLD_WARNING}")
            # ramp up monitoring and possibly schedule forecast
            # we set a temporary elevated flag in state
            # schedule forecast run in background (fire-and-forget)
            asyncio.create_task(forecast_and_report(region))
        else:
            # normal operating region
            if state.status != "NORMAL":
                state.status = "NORMAL"
                await notify_ops(region, f"Emissions returned to normal: {aggregate:.2f}")

        # record aggregate to history
        state.history.append({"ts": time.time(), "aggregate": aggregate, "status": state.status})


async def forecast_and_report(region: str):
    """
    Run a mock forecast and append result to state history and optionally notify.
    """
    # trivial throttle: wait a bit to mimic background processing
    await asyncio.sleep(random.uniform(0.1, 0.5))
    state = STATE[region]
    # simple linear forecast using last aggregate +/- noise
    last = state.last_aggregate or 50.0
    forecast = [round(last + (i * random.uniform(-1.0, 2.0)), 2) for i in range(6)]
    state.history.append({"ts": time.time(), "forecast_6h": forecast})
    # if forecast shows trend crossing critical, create early warning
    if any(val >= THRESHOLD_CRITICAL for val in forecast):
        await notify_ops(region, f"Forecast indicates critical emissions within 6h in {region}: {forecast}")
        # optionally create a pre-emptive ticket
        ticket = await create_incident(summary=f"Forecast critical emissions in {region}", region=region, severity="high")
        state.history.append({"forecast_ticket": ticket})


# --- Supervisor: create region state and run parallel tasks ---


async def start_region_monitor(region: str, stop_event: asyncio.Event):
    """
    Start sensor tasks and aggregator for a region. Returns when stop_event is set.
    """
    # init state
    STATE[region] = RegionState(region=region)
    # create sensor tasks
    sensor_stop = asyncio.Event()
    sensors = []
    for i in range(SENSOR_PER_REGION):
        sensor_id = f"{region}-sensor-{i+1}"
        coro = sensor_task(region, sensor_id, sensor_stop)
        sensors.append(asyncio.create_task(coro))
    # create aggregator
    agg_task = asyncio.create_task(aggregator_task(region, sensor_stop))

    try:
        # run until stop_event set
        await stop_event.wait()
    finally:
        # stop sensors and aggregator gracefully
        sensor_stop.set()
        # give them a moment to finish
        await asyncio.sleep(0.2)
        for t in sensors:
            t.cancel()
        agg_task.cancel()


async def main_monitor_run(runtime: int = 30):
    """
    Run all region monitors in parallel for 'runtime' seconds (demo).
    """
    stop_event = asyncio.Event()
    region_tasks = [asyncio.create_task(start_region_monitor(r, stop_event)) for r in REGIONS]

    # run for runtime seconds
    try:
        await asyncio.sleep(runtime)
    finally:
        print("[MAIN] stopping monitors...")
        stop_event.set()
        # wait small grace interval
        await asyncio.sleep(0.5)
        # cancel region tasks
        for t in region_tasks:
            t.cancel()

    # After stopping, print final state summary
    print("\n=== FINAL STATE SUMMARY ===")
    for r, s in STATE.items():
        print(f"- {r} status={s.status} last_agg={s.last_aggregate} tickets={len([h for h in s.history if 'ticket_id' in str(h)])}")


# --- Entrypoint for running the demo ---


if __name__ == "__main__":
    print("Starting Emission Monitoring Demo (parallel, branching, state mgmt)\n")
    # run the monitor for 45 seconds demo time
    asyncio.run(main_monitor_run(runtime=45))

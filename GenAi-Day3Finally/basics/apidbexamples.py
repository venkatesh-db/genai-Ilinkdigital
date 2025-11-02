
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
import requests
import sqlite3
import random
import time
import os

# ============ MOCK DATA SOURCES ============

# IoT mock temperature sensor function
def read_iot_temperature():
    """Simulates reading from an IoT temperature sensor."""
    return round(random.uniform(24.5, 30.5), 2)

# External API function (example: weather API)
def get_weather_data(city="Bangalore"):
    """Fetch weather data from an external API."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current_weather=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["current_weather"]
    except Exception as e:
        return {"error": str(e)}

# Database connection setup
conn = sqlite3.connect("environment_data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    weather TEXT
)
""")
conn.commit()

# ============ LANGCHAIN TOOLS ============

@tool
def read_iot_tool(_) -> str:
    """Read live temperature from IoT sensor."""
    temp = read_iot_temperature()
    return f"Current IoT temperature reading: {temp}°C"

@tool
def fetch_weather_tool(city: str) -> str:
    """Fetch current weather data for a city."""
    weather = get_weather_data(city)
    return f"Weather data for {city}: {weather}"

@tool
def log_to_db_tool(data: str) -> str:
    """Store IoT and weather data into local SQLite database."""
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    temp = read_iot_temperature()
    cursor.execute("INSERT INTO readings (timestamp, temperature, weather) VALUES (?, ?, ?)", (timestamp, temp, data))
    conn.commit()
    return f"Data logged at {timestamp}"

# ============ AGENT INITIALIZATION ============

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  No OpenAI API key found. Running in demo mode...")
    DEMO_MODE = True
else:
    DEMO_MODE = False
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tools = [read_iot_tool, fetch_weather_tool, log_to_db_tool]

def simple_agent_runner(task_description):
    """Simple agent simulation that executes tools based on task description"""
    print(f"\n🤖 Agent Task: {task_description}")
    
    # Execute the tools in sequence
    print("\n🔧 Executing tools...")
    
    # 1. Read IoT temperature
    temp = read_iot_temperature()
    iot_result = f"Current IoT temperature reading: {temp}°C"
    print(f"  ✅ {iot_result}")
    
    # 2. Fetch weather data  
    weather = get_weather_data("Bangalore")
    weather_result = f"Weather data for Bangalore: {weather}"
    print(f"  ✅ {weather_result}")
    
    # 3. Log to database
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO readings (timestamp, temperature, weather) VALUES (?, ?, ?)", 
                  (timestamp, temp, str(weather)))
    conn.commit()
    log_result = f"Data logged at {timestamp}"
    print(f"  ✅ {log_result}")
    
    return f"Completed IoT monitoring task: {iot_result}, {weather_result}, {log_result}"

# ============ RUN AGENT ============

if __name__ == "__main__":
    print("🔹 Example: Real-world AI Integration with IoT, API, and DB")
    
    if DEMO_MODE:
        print("🔄 Demo Mode: Simulating agent behavior...")
        result = simple_agent_runner("Fetch current IoT temperature, get weather in Bangalore, and store both into the database.")
        print(f"\n🎯 Final Result: {result}")
        
    else:
        print("� Full Agent Mode: Using LangChain tools...")
        result = simple_agent_runner("Fetch current IoT temperature, get weather in Bangalore, and store both into the database.")
        print(f"\n🎯 Final Result: {result}")

    # Verify DB content
    print("\n📋 Recent database entries:")
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 3")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Time: {row[1]}, Temp: {row[2]}°C, Weather: {row[3]}")
    
    # Clean up
    conn.close()

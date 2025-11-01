
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
import requests
import math

# -----------------------------
# Define Tools
# -----------------------------

# 1. Calculator Tool
def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}, "math": math})
        return f"The result is {result}"
    except Exception as e:
        return f"Error in calculation: {e}"

# 2. Weather Fetch Tool (uses a demo API)
def get_weather(city: str) -> str:
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url)
        if response.status_code == 200:
            return f"Weather info: {response.text}"
        else:
            return f"Could not fetch weather for {city}"
    except Exception as e:
        return f"Error fetching weather: {e}"

# -----------------------------
# Create LangChain Tools
# -----------------------------
tools = [
    Tool(
        name="Calculator",
        func=calculate,
        description="Useful for solving math expressions. Input example: '2 * (5 + 3)'"
    ),
    Tool(
        name="WeatherAPI",
        func=get_weather,
        description="Fetches current weather for a given city. Input example: 'Bangalore'"
    )
]

# -----------------------------
# Initialize LLM & Agent
# -----------------------------
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = initialize_agent(
    tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -----------------------------
# Run Multi-Tool Example
# -----------------------------
query = "Find today's weather in Delhi and then calculate 5 * (2 + 3)."

response = agent.run(query)

print("\n=== Final Response ===")
print(response)

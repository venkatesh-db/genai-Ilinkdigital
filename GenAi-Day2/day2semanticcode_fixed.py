from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain import hub
import random
import datetime
import os

# ========== Step 1: Define our Domain Functions (Tools) ==========

def analyze_energy_usage(location: str) -> str:
    """Simulates analysis of energy usage for a given location."""
    usage = random.randint(200, 800)
    return f"Energy usage in {location} is {usage} kWh today."

def forecast_energy_demand(location: str) -> str:
    """Forecasts next week's demand based on mock data."""
    forecast = random.randint(700, 1000)
    return f"Forecasted energy demand for next week in {location} is {forecast} kWh."

def recommend_action(forecast: str) -> str:
    """Recommends an energy optimization action."""
    # Extract the numeric value from the forecast string
    import re
    numbers = re.findall(r'\d+', forecast)
    if numbers:
        demand = int(numbers[0])
        if demand > 900:
            return "Recommendation: Enable smart grid load balancing and add solar input."
    return "Recommendation: Maintain current grid configuration."

# ========== Step 2: Create LangChain Tools ==========

tools = [
    Tool(
        name="EnergyUsageAnalyzer",
        func=analyze_energy_usage,
        description="Analyzes energy usage for a given location."
    ),
    Tool(
        name="EnergyDemandForecaster",
        func=forecast_energy_demand,
        description="Forecasts future energy demand."
    ),
    Tool(
        name="EnergyActionRecommender",
        func=recommend_action,
        description="Recommends optimization actions based on forecast data."
    ),
]

# ========== Demo version without API key ==========

def run_demo_without_api():
    """Demo version that runs without requiring OpenAI API key"""
    print(f"\n=== ENERGY ACTION PLANNER DEMO START ({datetime.date.today()}) ===")
    
    location = "Bangalore"
    
    # Step 1: Analyze current usage
    print("\n🔍 Step 1: Analyzing current energy usage...")
    usage_result = analyze_energy_usage(location)
    print(f"Result: {usage_result}")
    
    # Step 2: Forecast demand
    print("\n📈 Step 2: Forecasting energy demand...")
    forecast_result = forecast_energy_demand(location)
    print(f"Result: {forecast_result}")
    
    # Step 3: Get recommendations
    print("\n💡 Step 3: Getting optimization recommendations...")
    recommendation = recommend_action(forecast_result)
    print(f"Result: {recommendation}")
    
    print("\n✅ Energy optimization analysis complete!")

# ========== API Version (requires OpenAI API key) ==========

def run_with_api():
    """Full version with LangChain agent (requires API key)"""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it using: export OPENAI_API_KEY='your-api-key-here'")
        print("Running demo version instead...\n")
        run_demo_without_api()
        return

    try:
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        
        # Get the ReAct prompt from hub
        try:
            prompt = hub.pull("hwchase17/react")
        except:
            # Fallback prompt if hub is not available
            prompt = PromptTemplate.from_template("""
            Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}
            """)

        # Initialize the Agent
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Run the agent
        print(f"\n=== ENERGY ACTION PLANNER START ({datetime.date.today()}) ===")
        objective = "Optimize energy usage in Bangalore for next week. Analyze current usage, forecast demand, and provide recommendations."
        
        result = agent_executor.invoke({"input": objective})
        
        print("\n🧠 Agent Output:")
        print(result["output"])
        
    except Exception as e:
        print(f"❌ Error with API version: {e}")
        print("Running demo version instead...\n")
        run_demo_without_api()

# ========== Execute ==========

if __name__ == "__main__":
    print("🔋 Energy Management System")
    print("=" * 50)
    
    # Try API version first, fallback to demo if no API key
    run_with_api()
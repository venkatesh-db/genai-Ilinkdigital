
#Tool-Based Agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

# Define a tool
@tool
def get_weather(city: str) -> str:
    """Gets the current weather of a city."""
    return f"The weather in {city} is 28°C and sunny."

@tool
def get_time() -> str:
    """Gets the current time."""
    import datetime
    return f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}"

@tool
def calculate(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    try:
        # Simple calculator for basic operations
        result = eval(expression.replace('^', '**'))
        return f"Result: {result}"
    except:
        return "Error: Invalid expression"

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  No OpenAI API key found. Running in demo mode...")
    DEMO_MODE = True
else:
    DEMO_MODE = False

# LLM + Tools
if not DEMO_MODE:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tools = [get_weather, get_time, calculate]

def simple_tool_agent(query: str):
    """Simple tool-based agent that routes queries to appropriate tools"""
    print(f"\n🤖 Agent Query: {query}")
    
    query_lower = query.lower()
    
    # Route based on keywords
    if "weather" in query_lower:
        # Extract city name (simple approach)
        words = query.split()
        city = "Bangalore"  # default
        for i, word in enumerate(words):
            if word.lower() in ["in", "at", "for"] and i + 1 < len(words):
                city = words[i + 1].rstrip("?.,!")
                break
        
        result = get_weather.invoke({"city": city})
        print(f"🌤️  Weather Tool: {result}")
        return result
        
    elif "time" in query_lower:
        result = get_time.invoke({})
        print(f"🕐 Time Tool: {result}")
        return result
        
    elif any(op in query_lower for op in ["+", "-", "*", "/", "calculate", "compute", "math"]):
        # Extract mathematical expression
        expression = query
        for word in ["calculate", "compute", "what is", "what's"]:
            expression = expression.lower().replace(word, "").strip()
        expression = expression.rstrip("?.,!")
        
        result = calculate.invoke({"expression": expression})
        print(f"🧮 Calculator Tool: {result}")
        return result
        
    else:
        response = f"I can help with weather, time, or calculations. You asked: '{query}'"
        print(f"💬 General Response: {response}")
        return response

# Run Multiple Examples
if __name__ == "__main__":
    print("🔧 Tool-Based Agent - Multiple Capabilities Demo")
    print("=" * 50)
    
    # Test different types of queries
    test_queries = [
        "What's the weather in Bangalore?",
        "What's the weather in Mumbai?", 
        "What time is it?",
        "Calculate 15 + 25 * 2",
        "What is 100 / 4?",
        "Hello, how are you?"
    ]
    
    for query in test_queries:
        result = simple_tool_agent(query)
        print(f"✅ Final Answer: {result}\n")
        print("-" * 40)

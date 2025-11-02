from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType

# LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# Define tools
tools = [
    Tool(name="get_metrics", func=lambda region: {"region": region, "status": "OK"}, description="Fetch grid metrics"),
    Tool(name="forecast_demand", func=lambda hours: f"Forecast for {hours} hours", description="Forecast demand"),
]

# Initialize agent
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

# Run query
result = agent.run("Get north region grid metrics and forecast next 24 hours")
print(result)

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType

@tool
def calculator(expression: str) -> str:
    return str(eval(expression))

@tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

llm = ChatOpenAI(model="gpt-4o-mini")
tools = [calculator, greet]

agent = initialize_agent(tools, llm, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("Greet Venkatesh and then calculate 20 * 3")

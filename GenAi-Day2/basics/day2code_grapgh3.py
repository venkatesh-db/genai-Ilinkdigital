
from langgraph_prebuilt import create_node, create_graph

# Step 1: Define functions
def ask_name():
    name = input("What's your name? ")
    return name

def greet(name):
    return f"Hello, {name}! Welcome to LangGraph."

# Step 2: Create nodes
node1 = create_node("AskName", ask_name)
node2 = create_node("Greet", greet)

# Step 3: Build graph and connect nodes
graph = create_graph("GreetingGraph")
graph.add_node(node1)
graph.add_node(node2)
graph.connect(node1, node2)  # node1 output → node2 input

# Step 4: Run graph
result = graph.run()
print("Final Result:", result)

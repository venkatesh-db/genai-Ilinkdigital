

import random

# Example: Simulate random prompt selection for AI agent
prompts = [
    "Explain AI in 2 lines",
    "Summarize LangChain",
    "What is RAG in GenAI?"
]

selected_prompt = random.choice(prompts)
print("Selected prompt:", selected_prompt)

# Shuffle dataset before batching
dataset = list(range(1, 11))
random.shuffle(dataset)
print("Shuffled dataset:", dataset)

# Random float for stochastic AI sampling
rand_value = random.random()  # between 0 and 1
print("Random sampling value:", rand_value)



import os

# Example: List all Python files in current directory (for GenAI dataset loader)
current_dir = os.getcwd()
py_files = [f for f in os.listdir(current_dir) if f.endswith(".py")]
print(py_files)

# Create a new folder for AI logs if not exists
os.makedirs("ai_logs", exist_ok=True)
print("Directory 'ai_logs' ready!")

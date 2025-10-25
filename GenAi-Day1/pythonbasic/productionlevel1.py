
agent_name = "Nova"
agent_age = 2
agent_accuracy = 98.6
is_active = True

print(f"{agent_name} (v{agent_age}) accuracy: {agent_accuracy}% | Active: {is_active}")

agent_energy = 75
agent_focus = 88
print(f"Energy: {agent_energy}%, Focus: {agent_focus}%")

observations = ["face_detected", "object_recognized", "voice_command"]
observations.append("text_input")
print(observations)

agent_profile = {
    "name": "Orion",
    "skills": ["vision", "speech", "planning"],
    "performance": {"speed": 0.9, "accuracy": 0.95}
}
print(agent_profile["skills"][1])  # speech


memory = {"user_query": "What is AI?", "agent_response": "AI is machine intelligence."}
print(memory)

tasks = ["scan", "analyze", "respond"]
for task in tasks:
    print(f"Agent performing: {task}")


signals = ["start", "process", "update", "stop", "cleanup"]
for s in signals:
    if s == "stop":
        print("Agent stopping monitoring...")
        break
    print(f"Agent detected signal: {s}")


# Save agent log
with open("agent_log.txt", "w") as f:
    f.write("Agent started successfully.\n")

# Read log
with open("agent_log.txt", "r") as f:
    print(f.read())


chat_memory = {}

for i in range(3):
    user_input = input("User: ")
    response = f"Agent: I understood '{user_input}'."
    chat_memory[f"turn_{i+1}"] = {"user": user_input, "agent": response}
    print(response)

with open("chat_memory.txt", "w") as file:
    for turn, data in chat_memory.items():
        file.write(f"{turn}: {data}\n")

print("Chat saved successfully.")

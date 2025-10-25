
# Define a class
class AIModel:
    def __init__(self, name, accuracy):
        self.name = name
        self.accuracy = accuracy

    def __str__(self):
        return f"{self.name} ({self.accuracy}%)"

# Create array (list) of objects
models = [
    AIModel("GPT-4", 95),
    AIModel("Claude", 92),
    AIModel("LLaMA", 88)
]

# Loop through objects and print
for model in models:
    print(model)



# Find models with accuracy > 90
high_accuracy = [m for m in models if m.accuracy > 90]
print("High Accuracy Models:")
for m in high_accuracy:
    print(m)

# Output:
# High Accuracy Models:
# GPT-4 (95%)
# Claude (92%)


# List of objects
models = [
    AIModel("GPT-4", 95),
    AIModel("Claude", 92),
    AIModel("LLaMA", 88)
]


# Sort by accuracy descending
sorted_models = sorted(models, key=lambda m: m.accuracy, reverse=True)
for m in sorted_models:
    print(m)


# Output:
# GPT-4 (95%)
# Claude (92%)
# LLaMA (88%)


# Filter models with accuracy > 90 AND name starts with 'G'
filtered = [m for m in models if m.accuracy > 90 and m.name.startswith("G")]
for m in filtered:
    print("Filtered:", m)

# Output:
# Filtered: GPT-4 (95%)


# Boost accuracy for models < 90
for m in models:
    if m.accuracy < 90:
        m.accuracy += 5

for m in models:
    print("Updated:", m)

# Output:
# Updated: GPT-4 (95%)
# Updated: Claude (92%)
# Updated: LLaMA (93%)



texts = ["  hello AI!  ", "GENAI rocks.", "Python IS amazing"]

# Strip, lowercase, remove punctuation
cleaned = [t.strip().lower().replace("!", "") for t in texts]
print(cleaned)  # Output: ['hello ai', 'genai rocks.', 'python is amazing']

# Check if text contains 'genai'
contains_genai = [t for t in cleaned if "genai" in t]
print(contains_genai)  # Output: ['genai rocks.']


# Example: Tokenize sentences for a model input
sentences = ["GenAI is powerful.", "Python makes life easier.", "Async helps performance."]

tokenized = []
for sentence in sentences:
    tokens = sentence.lower().split()  # lowercase + split
    tokenized.append(tokens)

print(tokenized)
# Output: [['genai', 'is', 'powerful.'], ['python', 'makes', 'life', 'easier.'], ['async', 'helps', 'performance.']]





# Example: Preprocessing token lengths for AI input
sentences = [
    "GenAI is transforming the world.",
    "Python makes AI pipelines easy.",
    "Async programming improves performance."
]

# List comprehension: compute token counts
token_counts = [len(s.split()) for s in sentences]
print(token_counts)  # Output: [5, 6, 5]

# Filter sentences with more than 5 tokens
long_sentences = [s for s in sentences if len(s.split()) > 5]
print(long_sentences)  # Output: ['Python makes AI pipelines easy.']



# Example: Compute embedding length or similarity score
embeddings = [0.5, 0.8, 0.3, 0.9]

# Lambda to normalize embeddings between 0 and 1
normalize = lambda x: x / max(embeddings)
normalized = list(map(normalize, embeddings))
print(normalized)  # Output: [0.555..., 0.888..., 0.333..., 1.0]

# Lambda with filter: select embeddings > 0.5
high_embeddings = list(filter(lambda x: x > 0.5, embeddings))
print(high_embeddings)  # Output: [0.8, 0.9]



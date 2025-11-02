
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

print("🎨 Dynamic Creative Writing Prompts")
print("=" * 45)

# 1️⃣ Define a prompt template with placeholders
template = """
You are a creative writer.
Write a {tone} paragraph about {topic}.
"""
prompt = PromptTemplate(
    template=template,
    input_variables=["tone", "topic"]
)

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY not set!")
    print("🎭 Demo Mode: Showing dynamic prompt examples...")
    
    # Show how dynamic prompts work
    scenarios = [
        {"tone": "funny", "topic": "AI learning human emotions"},
        {"tone": "serious", "topic": "climate change"},
        {"tone": "mysterious", "topic": "deep ocean exploration"}
    ]
    
    print(f"\n📝 Template: {template.strip()}")
    print(f"🔧 Variables: {prompt.input_variables}")
    
    for i, scenario in enumerate(scenarios, 1):
        formatted_prompt = prompt.format(**scenario)
        print(f"\n--- Example {i} ---")
        print(f"Input: {scenario}")
        print(f"Generated prompt: {formatted_prompt.strip()}")
    
    print(f"\n💡 To run with AI generation:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    exit(0)

# Full mode with API
try:
    # 2️⃣ Initialize the model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # 3️⃣ Define different scenarios to test
    scenarios = [
        {"tone": "funny", "topic": "AI learning human emotions"},
        {"tone": "serious", "topic": "climate change"},
        {"tone": "poetic", "topic": "morning coffee ritual"},
        {"tone": "suspenseful", "topic": "abandoned space station"}
    ]
    
    # 4️⃣ Run with different values dynamically
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario}")
        print("-" * 40)
        
        formatted_prompt = prompt.format(**scenario)
        response = llm.invoke(formatted_prompt)
        
        print(f"📝 Generated Content:")
        print(response.content)
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("This might be due to API key issues or network problems.")

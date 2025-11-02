
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

print("🎭 Poetry Generator with Prompts")
print("=" * 40)

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY not set!")
    print("🎨 Demo Mode: Showing prompt structure...")
    
    # Step 1: Define the prompt template
    template = "Write a short poem about {topic} in {style} style."
    prompt = PromptTemplate(template=template, input_variables=["topic", "style"])
    
    # Show how the prompt works
    demo_prompt = prompt.format(topic="coding", style="romantic")
    print(f"\n📝 Template: {template}")
    print(f"🔧 Variables: {prompt.input_variables}")
    print(f"✨ Formatted prompt: {demo_prompt}")
    
    print(f"\n💡 To run with AI generation:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    exit(0)

# Full mode with API
try:
    # Step 1: Define the prompt template
    template = "Write a short poem about {topic} in {style} style."
    prompt = PromptTemplate(template=template, input_variables=["topic", "style"])

    # Step 2: Load the model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Step 3: Create and run the chain (modern approach)
    formatted_prompt = prompt.format(topic="coding", style="romantic")
    print(f"🎯 Generated prompt: {formatted_prompt}")
    
    response = llm.invoke(formatted_prompt)
    
    print(f"\n🤖 AI Generated Poem:")
    print(response.content)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("This might be due to API key issues or network problems.")

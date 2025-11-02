
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

print("🔄 Multi-Step AI Processing Pipeline")
print("=" * 45)

# Input text
input_text = "Artificial intelligence is transforming industries by automating routine tasks, \
enhancing decision-making, and creating new possibilities for innovation."

print(f"📝 Input Text:\n{input_text}\n")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY not set!")
    print("🎭 Demo Mode: Showing multi-step pipeline structure...")
    
    # Step 1️⃣: Show Summary step
    summary_prompt = PromptTemplate.from_template(
        "Summarize this paragraph in one line:\n\n{text}"
    )
    step1_formatted = summary_prompt.format(text=input_text)
    print("🔸 Step 1 - Summary Prompt:")
    print(step1_formatted)
    
    # Step 2️⃣: Show Translation step
    translate_prompt = PromptTemplate.from_template(
        "Translate this English text to Tamil:\n\n{summary}"
    )
    demo_summary = "AI is revolutionizing industries through automation and innovation."
    step2_formatted = translate_prompt.format(summary=demo_summary)
    print(f"\n🔸 Step 2 - Translation Prompt:")
    print(step2_formatted)
    
    print(f"\n💡 To run full AI pipeline:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    exit(0)

# Full mode with API
try:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
    
    # Step 1️⃣: Summarize text
    print("🔄 Step 1: Summarizing text...")
    summary_prompt = PromptTemplate.from_template(
        "Summarize this paragraph in one line:\n\n{text}"
    )
    
    step1_formatted = summary_prompt.format(text=input_text)
    step1_response = llm.invoke(step1_formatted)
    summary = step1_response.content
    
    print(f"✅ Summary: {summary}")
    
    # Step 2️⃣: Translate the summary to Tamil
    print(f"\n🔄 Step 2: Translating to Tamil...")
    translate_prompt = PromptTemplate.from_template(
        "Translate this English text to Tamil:\n\n{summary}"
    )
    
    step2_formatted = translate_prompt.format(summary=summary)
    step2_response = llm.invoke(step2_formatted)
    tamil_translation = step2_response.content
    
    print(f"✅ Tamil Translation: {tamil_translation}")
    
    # Final Output
    print(f"\n🎯 Pipeline Complete!")
    print("=" * 45)
    print(f"📥 Original: {input_text}")
    print(f"📊 Summary: {summary}")
    print(f"🔤 Tamil: {tamil_translation}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("This might be due to API key issues or network problems.")

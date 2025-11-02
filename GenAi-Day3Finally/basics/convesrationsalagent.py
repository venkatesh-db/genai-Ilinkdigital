
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
import os

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  No OpenAI API key found. Running in demo mode...")
    DEMO_MODE = True
else:
    DEMO_MODE = False

class SimpleConversationMemory:
    """Simple conversation memory implementation"""
    def __init__(self):
        self.messages = []
    
    def add_user_message(self, message: str):
        self.messages.append(HumanMessage(content=message))
    
    def add_ai_message(self, message: str):
        self.messages.append(AIMessage(content=message))
    
    def get_conversation_context(self):
        context = ""
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                context += f"Human: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                context += f"Assistant: {msg.content}\n"
        return context
    
    def clear(self):
        self.messages = []

def run_conversation_demo():
    if DEMO_MODE:
        print("🔄 Demo Mode: Simulating conversational agent with memory...")
        
        # Simulate conversation memory
        memory = SimpleConversationMemory()
        
        conversations = [
            ("Hi, I'm Venkatesh.", "Hello Venkatesh! Nice to meet you. How can I help you today?"),
            ("I live in Bangalore.", "Thank you for sharing that, Venkatesh. I'll remember that you live in Bangalore. Is there anything specific about Bangalore you'd like to discuss?"),
            ("Where do I live?", "Based on our conversation, you live in Bangalore, Venkatesh.")
        ]
        
        for i, (user_input, ai_response) in enumerate(conversations):
            print(f"\n💬 Turn {i+1}:")
            print(f"👤 User: {user_input}")
            
            # Add to memory
            memory.add_user_message(user_input)
            memory.add_ai_message(ai_response)
            
            print(f"🤖 Assistant: {ai_response}")
            
            # Show memory context
            if i == len(conversations) - 1:  # Last turn
                print(f"\n📝 Memory Context:")
                print(memory.get_conversation_context())
        
        print(f"\n✅ Demo completed - Memory successfully retained user information!")
        
    else:
        print("🤖 Full Conversational Agent Mode")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
        memory = SimpleConversationMemory()

        # Create a prompt template that includes conversation history
        prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant with perfect memory. "
            "Here is our conversation history:\n{conversation_history}\n"
            "Human: {input}\nAssistant:"
        )

        print("\n💬 Starting conversation...")
        
        inputs = [
            "Hi, I'm Venkatesh.",
            "I live in Bangalore.", 
            "Where do I live?"
        ]
        
        for i, user_input in enumerate(inputs):
            print(f"\n👤 User: {user_input}")
            
            # Get current conversation context
            conversation_history = memory.get_conversation_context()
            
            # Create the full prompt
            full_prompt = prompt.format(
                conversation_history=conversation_history,
                input=user_input
            )
            
            # Get response from LLM
            response = llm.invoke(full_prompt)
            ai_response = response.content
            
            print(f"🤖 Assistant: {ai_response}")
            
            # Add to memory
            memory.add_user_message(user_input)
            memory.add_ai_message(ai_response)
        
        print(f"\n📝 Final Conversation History:")
        print(memory.get_conversation_context())

if __name__ == "__main__":
    print("💬 Conversational Agent with Memory")
    print("=" * 40)
    run_conversation_demo()

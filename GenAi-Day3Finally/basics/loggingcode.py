
import logging
from datetime import datetime

# ========== 1️⃣ Setup Logging ==========
logging.basicConfig(
    filename="ai_system.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ========== 2️⃣ Safe Prompt Filter ==========
def sanitize_input(prompt: str) -> str:
    """
    Sanitize user input to prevent unsafe or unethical prompts.
    """
    banned_words = ["hack", "weapon", "bypass", "violence", "racism"]
    for word in banned_words:
        if word in prompt.lower():
            logging.warning(f"Blocked unethical input: {prompt}")
            raise ValueError("⚠️ Unsafe or unethical content detected.")
    return prompt.strip()

# ========== 3️⃣ Mock AI Response Function ==========
def ethical_ai_response(prompt: str) -> str:
    """
    Mock AI engine that respects ethical and safe prompting.
    """
    prompt = sanitize_input(prompt)
    logging.info(f"Received safe prompt: {prompt}")

    # Simulate AI reasoning (placeholder)
    if "bank" in prompt.lower():
        response = "Banks must ensure customer data protection and financial transparency."
    elif "college" in prompt.lower():
        response = "Education empowers individuals to contribute positively to society."
    else:
        response = "Let's discuss constructive and ethical topics only."
    
    logging.info(f"Generated response: {response}")
    return response

# ========== 4️⃣ Main Execution ==========
if __name__ == "__main__":
    try:
        user_prompt = input("Enter your question for AI: ")
        answer = ethical_ai_response(user_prompt)
        print(f"\n🤖 AI Response: {answer}\n")

    except ValueError as e:
        print(str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print("❌ Something went wrong. Logged for review.")

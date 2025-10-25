'''
Flow of code 

1.     
2.  
3.   
4.   
5.   
6.   
7. 

-
'''



# banking_qna_new.py
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.schema.runnable import Runnable


class MockLLM(Runnable):
    def invoke(self, prompt: str, config=None, **kwargs):
        if "KYC" in prompt:
            return "KYC ensures banks verify identity to prevent fraud and money laundering."
        elif "AML" in prompt:
            return "AML requires monitoring of transactions to detect suspicious activity."
        elif "Basel III" in prompt:
            return "Basel III mandates capital adequacy, liquidity ratios, and leverage limits."
        else:
            return "Banks must comply with RBI and global risk management regulations."

class PromptFormatter(Runnable):
    def __init__(self, template: str):
        self.template = template

    # Accept config as second argument
    def invoke(self, inputs, config=None, **kwargs):
        return self.template.format(**inputs)

template = """
You are a banking compliance assistant.
Answer questions about banking regulations in 2-3 sentences.

Question: {question}
"""

prompt_runnable = PromptFormatter(template)
llm = MockLLM()

# Pass Runnables as separate arguments
chain = RunnableSequence(prompt_runnable, llm)

questions = [
    "What is KYC and why is it important?",
    "Explain AML compliance for Indian banks.",
    "Describe Basel III norms in simple terms.",
    "How do RBI guidelines affect customer data protection?"
]

for q in questions:
    answer = chain.invoke({"question": q})
    print(f"Q: {q}\nA: {answer}\n")

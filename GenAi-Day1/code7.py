
'''
Flow of code 

1.   design a function with mock stock news data.   
2.   design two class MockSummarizer ,PromptRunnable   inherit  Runnable 
3.    MockSummarizer invoke method
      --input_text.split
      --  loop and conditions to generate natural-language summary
4.    PromptRunnable invoke method  self.template.format(**inputs)
5.   
6.   
7.  inovke mock news function, execution differnece PromptRunnable , MockSummarizer
8.  agent_chain.invoke 

-
'''

# filename: stock_news_agent_improved.py
import random
from langchain_core.runnables.base import Runnable, RunnableSequence

# --------------------------
# Step 1: Mock News Fetcher
# --------------------------
def fetch_stock_news():
    news = [
        "Tech stocks surge as Nasdaq hits record high.",
        "Oil prices stabilize after global supply concerns.",
        "Bitcoin rises 5% following regulatory updates.",
        "Investors react positively to quarterly earnings reports."
    ]
    # Return exactly 3 random news items
    return random.sample(news, 3)

# --------------------------
# Step 2: Mock Summarizer (Runnable)
# --------------------------
class MockSummarizer(Runnable):
    def invoke(self, input_text: str, config=None, **kwargs):
        # Extract news content after "News Articles:"
        if "News Articles:" in input_text:
            news_text = input_text.split("News Articles:")[1].strip()
        else:
            news_text = input_text

        sentences = [s.strip() for s in news_text.split(".") if s.strip()]

        # Natural-language summary: join with commas and "and" for last item
        if not sentences:
            return "No news to summarize."
        elif len(sentences) == 1:
            return sentences[0] + "."
        elif len(sentences) == 2:
            return ". ".join(sentences) + "."
        else:
            return ", ".join(sentences[:-1]) + ", and " + sentences[-1] + "."

# --------------------------
# Step 3: Prompt Wrapper (Runnable)
# --------------------------
class PromptRunnable(Runnable):
    def __init__(self, template: str):
        self.template = template

    def invoke(self, inputs: dict, config=None, **kwargs):
        # inputs must be a dict with key "news"
        if not isinstance(inputs, dict):
            raise TypeError("PromptRunnable expects a dict input")
        return self.template.format(**inputs)

# --------------------------
# Step 4: RunnableSequence
# --------------------------
template_text = (
    "You are a stock market assistant.\n"
    "Summarize the following news articles in 2-3 concise sentences.\n\n"
    "News Articles: {news}"
)
prompt_runnable = PromptRunnable(template_text)
summarizer = MockSummarizer()

# Pass runnables as separate args (not a list)
agent_chain = RunnableSequence(prompt_runnable, summarizer)

# --------------------------
# Step 5: Run Demo
# --------------------------
if __name__ == "__main__":
    articles = fetch_stock_news()
    news_text = " ".join(articles)

    summary = agent_chain.invoke({"news": news_text})

    print("\n=== Stock Market News Summarization Agent ===\n")
    print("Original News Articles:\n")
    for a in articles:
        print("-", a)
    print("\nSummary:\n", summary)

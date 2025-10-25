'''
import asyncio
import random

async def fetch_data(api_name):
    print(f"🔹 Fetching data from {api_name}...")
    await asyncio.sleep(random.uniform(1, 3))  # simulate delay
    print(f"✅ Finished fetching from {api_name}")
    return f"Data from {api_name}"

async def main():
    apis = ["OpenAI", "LangChain", "HuggingFace"]
    tasks = [fetch_data(api) for api in apis]
    results = await asyncio.gather(*tasks)
    print("📦 All Results:", results)

asyncio.run(main())

'''


import asyncio
from abc import ABC, abstractmethod

# --- Base Async Runnable Interface ---
class Runnable(ABC):
    @abstractmethod
    async def invoke(self, input_data):
        pass


class SentimentAnalyzer(Runnable):
    async def invoke(self, input_data):
        await asyncio.sleep(2)
        return f"[SentimentAnalyzer] '{input_data}' → Positive"


class KeywordExtractor(Runnable):
    async def invoke(self, input_data):
        await asyncio.sleep(1)
        return f"[KeywordExtractor] Extracted keywords from: '{input_data}'"


# --- Execute all Async Runnables in Parallel ---
async def execute_runnables(runnables, input_data):
    tasks = [r.invoke(input_data) for r in runnables]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)


# --- Main entry ---
async def main():
    runnables = [SentimentAnalyzer(), KeywordExtractor()]
    await execute_runnables(runnables, "LangChain makes AI pipelines easy!")

asyncio.run(main())



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


import asyncio
from semantic_kernel.functions import kernel_function

# Define the native function
@kernel_function(
    description="Summarizes trading reports concisely",
    name="SummarizeTradingReport"
)
async def summarize_report(ctx):
    report = ctx["report"]
    sentences = report.split(".")
    summary = ". ".join(sentence.strip() for sentence in sentences[:2]) + "."
    return summary

# Async main function
async def main():
    trading_report = """
    Today, the stock market saw a strong rally with tech stocks leading the gains.
    Bitcoin prices rose by 5% after positive regulatory news.
    Oil prices remained steady amid supply concerns.
    Trading volume was higher than average, signaling strong investor interest.
    """
    
    # Call the async function directly
    summary = await summarize_report({"report": trading_report})

    print("\n=== Trading Report Summary (Demo Mode) ===\n")
    print(summary)

# Run the async main
if __name__ == "__main__":
    asyncio.run(main())

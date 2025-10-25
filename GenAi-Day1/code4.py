

'''
Flow of code 

1.   import packages asyncio, aiohttp, os, random    
2.   load environment variables for API keys with default "demo" values
3.   laod fake demo URLs for stock and crypto APIs
4.   async function fetch_json to simulate fetching JSON data with random delay 
5.   fetch_stock_price function to get stock prices (mock if demo key)
6.   fetch_crypto_price function to get crypto prices (mock if demo key)
7.   execution of main async routine to fetch and display prices
8.   loops dsa to fetch_stock_price and fetch_crypto_price concurrently

-
'''


import asyncio
import aiohttp
import os
import random

# Load environment variables (demo keys)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
COINAPI_KEY = os.getenv("COINAPI_KEY", "demo")

# Fake demo URLs (for structure only)
STOCK_URL = "https://demo.alphavantage.co/query"
CRYPTO_URL = "https://demo.coinapi.io/v1/exchangerate"

# Asynchronous fetch simulation
async def fetch_json(session, url, headers=None):
    # Simulate network delay
    await asyncio.sleep(random.uniform(0.5, 1.5))
    # Return mock data instead of real API response
    return {"price": round(random.uniform(100, 50000), 2)}

# Stock price fetcher (demo)
async def fetch_stock_price(session, symbol):
    if ALPHA_VANTAGE_API_KEY == "demo":
        print(f"[INFO] Fetching mock stock data for {symbol}")
        await asyncio.sleep(1)
        return {symbol: round(random.uniform(100, 1000), 2)}
    else:
        url = f"{STOCK_URL}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        data = await fetch_json(session, url)
        return {symbol: data.get("price", "Unavailable")}

# Crypto price fetcher (demo)
async def fetch_crypto_price(session, symbol):
    if COINAPI_KEY == "demo":
        print(f"[INFO] Fetching mock crypto data for {symbol}")
        await asyncio.sleep(1)
        return {symbol: round(random.uniform(20000, 60000), 2)}
    else:
        url = f"{CRYPTO_URL}/{symbol}/USD"
        headers = {"X-CoinAPI-Key": COINAPI_KEY}
        data = await fetch_json(session, url, headers=headers)
        return {symbol: data.get("price", "Unavailable")}

# Main async routine
async def main():
    stocks = ["AAPL", "GOOGL"]
    cryptos = ["BTC", "ETH"]

    async with aiohttp.ClientSession() as session:
        stock_tasks = [fetch_stock_price(session, s) for s in stocks]
        crypto_tasks = [fetch_crypto_price(session, c) for c in cryptos]

        results = await asyncio.gather(*stock_tasks, *crypto_tasks)

    print("\n=== Live Market Prices (Demo Mode) ===")
    for result in results:
        for name, price in result.items():
            print(f"{name}: ${price}")

# Run program
if __name__ == "__main__":
    asyncio.run(main())

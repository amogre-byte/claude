"""
Quick test for get_bulk_prices tool.
Run this directly to verify the tool works before wiring it into the MCP server.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bloomberg_client import BloombergClient
from tools.prices import get_bulk_prices

client = BloombergClient()
tool = get_bulk_prices(client)

tickers = ["AAPL US Equity", "MSFT US Equity", "NVDA US Equity", "INVALID TICKER"]
print(f"Fetching prices for: {tickers}\n")

results = tool(tickers)

for ticker, value in results.items():
    print(f"  {ticker:<25} {value}")

client.disconnect()

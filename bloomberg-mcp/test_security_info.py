"""
Quick test for get_security_info tool.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bloomberg_client import BloombergClient
from tools.security_info import get_security_info

client = BloombergClient()
tool = get_security_info(client)

ticker = "AAPL US Equity"
print(f"Fetching security info for: {ticker}\n")

result = tool(ticker)

for field, value in result.items():
    print(f"  {field:<25} {value}")

client.disconnect()

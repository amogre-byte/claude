"""
Quick test for get_historical_data tool.
Fetches daily PX_LAST for AAPL over the past year.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bloomberg_client import BloombergClient
from tools.historical import get_historical_data

client = BloombergClient()
tool = get_historical_data(client)

ticker     = "AAPL US Equity"
start_date = "20250101"
end_date   = "20260524"

print(f"Fetching daily PX_LAST for {ticker} from {start_date} to {end_date}...\n")

records = tool(ticker, start_date, end_date)

if isinstance(records, dict) and "error" in records:
    print(f"ERROR: {records['error']}")
else:
    print(f"  {'Date':<12} {'PX_LAST':>10}")
    print(f"  {'-'*12} {'-'*10}")
    for r in records:
        print(f"  {r['date']:<12} {r.get('PX_LAST', 'N/A'):>10}")
    print(f"\n  Total records: {len(records)}")

client.disconnect()

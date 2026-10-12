"""
Bloomberg MCP Server
Exposes Bloomberg Terminal data as MCP tools for Claude.
"""

from mcp.server.fastmcp import FastMCP
from bloomberg_client import BloombergClient
from tools.prices import get_bulk_prices
from tools.historical import get_historical_data
from tools.security_info import get_security_info
from tools.news import get_recent_company_news
from tools.comps import get_comparable_analysis
from tools.financials import get_financial_statements

# Initialise the MCP server
mcp = FastMCP("Bloomberg Terminal")

# Shared Bloomberg client (one session, reused across tools)
client = BloombergClient()

# Register tools
mcp.tool()(get_bulk_prices(client))
mcp.tool()(get_historical_data(client))
mcp.tool()(get_security_info(client))
mcp.tool()(get_recent_company_news(client))
mcp.tool()(get_comparable_analysis(client))
mcp.tool()(get_financial_statements(client))

if __name__ == "__main__":
    mcp.run()

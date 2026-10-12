"""
Tool: get_bulk_prices
Returns the current last price for a list of securities.
"""

from bloomberg_client import BloombergClient


def get_bulk_prices(client: BloombergClient):
    def get_bulk_prices(tickers: list[str]) -> dict:
        """
        Get the current last price for one or more Bloomberg securities.

        Args:
            tickers: List of Bloomberg tickers, e.g. ["AAPL US Equity", "MSFT US Equity"]

        Returns:
            Dict mapping each ticker to its last price, or an error message if not found.
            Example: {"AAPL US Equity": 308.82, "MSFT US Equity": 415.10}
        """
        client.ensure_connected()

        # Build request
        request = client.ref_data_service.createRequest("ReferenceDataRequest")
        for ticker in tickers:
            request.append("securities", ticker)
        request.append("fields", "PX_LAST")

        # Send and collect responses
        messages = client.send_request(request)

        # Parse results
        results = {}
        for msg in messages:
            if not msg.hasElement("securityData"):
                continue
            security_data = msg.getElement("securityData")
            for i in range(security_data.numValues()):
                security = security_data.getValue(i)
                ticker = security.getElementAsString("security")

                # Check for security-level errors (e.g. invalid ticker)
                if security.hasElement("securityError"):
                    error = security.getElement("securityError")
                    results[ticker] = f"ERROR: {error.getElementAsString('message')}"
                    continue

                field_data = security.getElement("fieldData")
                if field_data.hasElement("PX_LAST"):
                    results[ticker] = field_data.getElementAsFloat("PX_LAST")
                else:
                    results[ticker] = "N/A"

        return results

    return get_bulk_prices

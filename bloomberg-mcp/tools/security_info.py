"""
Tool: get_security_info
Returns reference/static data for a security (name, sector, currency, etc.)
"""

from bloomberg_client import BloombergClient

DEFAULT_FIELDS = [
    "NAME",
    "SECURITY_TYP",
    "GICS_SECTOR_NAME",
    "CRNCY",
    "COUNTRY_FULL_NAME",
    "MARKET_SECTOR_DES",
    "EQY_SH_OUT",
    "CUR_MKT_CAP",
]


def get_security_info(client: BloombergClient):
    def get_security_info(ticker: str, fields: list[str] = DEFAULT_FIELDS) -> dict:
        """
        Get reference/static data for a Bloomberg security.

        Args:
            ticker: Bloomberg ticker, e.g. "AAPL US Equity"
            fields: List of Bloomberg reference fields to fetch.

        Returns:
            Dict of {field: value} for the requested security.
        """
        client.ensure_connected()

        # Build request
        request = client.ref_data_service.createRequest("ReferenceDataRequest")
        request.append("securities", ticker)
        for field in fields:
            request.append("fields", field)

        # Send and collect responses
        messages = client.send_request(request)

        # Parse results
        result = {}
        for msg in messages:
            if not msg.hasElement("securityData"):
                continue
            security_data = msg.getElement("securityData")
            for i in range(security_data.numValues()):
                security = security_data.getValue(i)

                if security.hasElement("securityError"):
                    error = security.getElement("securityError")
                    return {"error": error.getElementAsString("message")}

                field_data = security.getElement("fieldData")
                for field in fields:
                    if field_data.hasElement(field):
                        element = field_data.getElement(field)
                        # Handle different value types
                        try:
                            result[field] = element.getValueAsFloat()
                        except Exception:
                            try:
                                result[field] = element.getValueAsString()
                            except Exception:
                                result[field] = "N/A"
                    else:
                        result[field] = "N/A"

        return result

    return get_security_info

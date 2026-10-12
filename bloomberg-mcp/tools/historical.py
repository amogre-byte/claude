"""
Tool: get_historical_data
Returns daily field data for a security over a date range.
"""

from bloomberg_client import BloombergClient


def get_historical_data(client: BloombergClient):
    def get_historical_data(ticker: str, start_date: str, end_date: str, fields: list[str] = ["PX_LAST"]) -> dict:
        """
        Get historical daily data for a Bloomberg security.

        Args:
            ticker:     Bloomberg ticker, e.g. "AAPL US Equity"
            start_date: Start date in YYYYMMDD format, e.g. "20240101"
            end_date:   End date in YYYYMMDD format, e.g. "20241231"
            fields:     List of Bloomberg fields, default ["PX_LAST"].
                        Common options: PX_LAST, PX_OPEN, PX_HIGH, PX_LOW, PX_VOLUME

        Returns:
            List of {date, field: value} records ordered oldest to newest.
        """
        client.ensure_connected()

        # Build request
        request = client.ref_data_service.createRequest("HistoricalDataRequest")
        request.append("securities", ticker)
        for field in fields:
            request.append("fields", field)
        request.set("startDate", start_date)
        request.set("endDate", end_date)
        request.set("periodicitySelection", "DAILY")

        # Send and collect responses
        messages = client.send_request(request)

        # Parse results — HistoricalDataRequest returns a single securityData element
        records = []
        for msg in messages:
            if not msg.hasElement("securityData"):
                continue

            security_data = msg.getElement("securityData")

            if security_data.hasElement("securityError"):
                error = security_data.getElement("securityError")
                return {"error": error.getElementAsString("message")}

            field_data_array = security_data.getElement("fieldData")

            for i in range(field_data_array.numValues()):
                row = field_data_array.getValue(i)
                record = {"date": str(row.getElementAsDatetime("date"))}
                for field in fields:
                    if row.hasElement(field):
                        try:
                            record[field] = row.getElementAsFloat(field)
                        except Exception:
                            record[field] = row.getElementAsString(field)
                    else:
                        record[field] = None
                records.append(record)

        return records

    return get_historical_data

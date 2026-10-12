import blpapi

def test_bloomberg_connection():
    # Session options - connects to local Bloomberg Terminal
    session_options = blpapi.SessionOptions()
    session_options.setServerHost("localhost")
    session_options.setServerPort(8194)

    print("Connecting to Bloomberg Terminal...")
    session = blpapi.Session(session_options)

    if not session.start():
        print("ERROR: Failed to start session. Is Bloomberg Terminal running?")
        return

    print("Session started successfully.")

    if not session.openService("//blp/refdata"):
        print("ERROR: Failed to open reference data service.")
        session.stop()
        return

    print("Reference data service opened.")

    # Request PX_LAST for AAPL US Equity
    ref_data_service = session.getService("//blp/refdata")
    request = ref_data_service.createRequest("ReferenceDataRequest")
    request.append("securities", "AAPL US Equity")
    request.append("fields", "PX_LAST")
    request.append("fields", "NAME")

    print("\nRequesting data for AAPL US Equity...")
    session.sendRequest(request)

    # Process response
    while True:
        event = session.nextEvent(500)
        for msg in event:
            if msg.hasElement("securityData"):
                security_data = msg.getElement("securityData")
                for i in range(security_data.numValues()):
                    security = security_data.getValue(i)
                    ticker = security.getElementAsString("security")
                    field_data = security.getElement("fieldData")
                    name = field_data.getElementAsString("NAME")
                    price = field_data.getElementAsFloat("PX_LAST")
                    print(f"\n✓ Connection successful!")
                    print(f"  Ticker : {ticker}")
                    print(f"  Name   : {name}")
                    print(f"  Price  : {price}")

        if event.eventType() == blpapi.Event.RESPONSE:
            break

    session.stop()
    print("\nSession closed.")

if __name__ == "__main__":
    test_bloomberg_connection()

import requests
import os

def ingest_data():
    """
    Connects to Eventbrite API and fetches event data.
    Stores/prints results (placeholder: prints to console).
    """
    api_token = os.getenv("EVENTBRITE_API_TOKEN")
    if not api_token:
        print("[!] EVENTBRITE_API_TOKEN not set in environment variables.")
        return

    headers = {"Authorization": f"Bearer {api_token}"}
    url = "https://www.eventbriteapi.com/v3/events/search/"

    try:
        response = requests.get(url, headers=headers, params={"q": "technology"})
        response.raise_for_status()
        data = response.json()

        events = data.get("events", [])
        print(f"[+] Retrieved {len(events)} events from Eventbrite")
        for event in events[:5]:  # show only top 5
            print(f"  - {event['name']['text']}")

    except Exception as e:
        print(f"[!] Error fetching Eventbrite data: {e}")


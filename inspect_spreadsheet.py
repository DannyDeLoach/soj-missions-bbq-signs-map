import requests
import json
from pprint import pprint

# The URL for the Google Apps Script bridge found in index.html
SYNC_URL = "https://script.google.com/macros/s/AKfycbyaRAWhjH6a_XBsV-6JWwVtFFOyBySi3MNV9eO8CfdcIxWbjrzAfke5hFP0m0lOeRUE/exec"

def fetch_spreadsheet_data():
    """
    Fetches the sign data from the Google Apps Script web app.
    """
    print(f"Connecting to: {SYNC_URL}...")
    try:
        response = requests.get(SYNC_URL)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n--- Current Spreadsheet Data (JSON) ---")
        if isinstance(data, dict):
            # If it's a keyed object {id: {data}}
            for sign_id, details in data.items():
                print(f"ID: {sign_id}")
                pprint(details)
                print("-" * 20)
        elif isinstance(data, list):
            # If it's an array of objects [{id: ..., data: ...}]
            for item in data:
                pprint(item)
                print("-" * 20)
        else:
            pprint(data)
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_spreadsheet_data()

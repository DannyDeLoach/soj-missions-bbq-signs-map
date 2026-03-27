import os
from googleapiclient.discovery import build
from my_library import get_google_credentials

def find_spreadsheet():
    creds = get_google_credentials()
    if not creds:
        print("Failed to get credentials.")
        return None

    # Use Drive API to search for the spreadsheet
    drive_service = build('drive', 'v3', credentials=creds)
    
    query = "name contains 'Missions BBQ' and mimeType = 'application/vnd.google-apps.spreadsheet'"
    print(f"Searching for spreadsheets with query: {query}")
    
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print("No spreadsheets found.")
        return None
    
    print("\nFound the following spreadsheets:")
    for item in items:
        print(f"- {item['name']} (ID: {item['id']})")
    
    return items[0]['id']

if __name__ == "__main__":
    find_spreadsheet()

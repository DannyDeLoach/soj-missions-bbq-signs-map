import datetime
import json
from googleapiclient.discovery import build
from my_library import get_google_credentials

# Configuration
SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI'

def reformat_spreadsheet():
    creds = get_google_credentials()
    if not creds:
        return
    
    service = build('sheets', 'v4', credentials=creds)
    
    # 1. Get the current sheet name
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    original_sheet_name = 'Status'
    
    # List sheets to find the backup name
    sheets = [s['properties']['title'] for s in spreadsheet['sheets']]
    backup_name = next((s for s in sheets if s.startswith('Backup_')), None)
    
    if not backup_name:
        print("No backup found to restore from.")
        return

    print(f"Reading data from backup: {backup_name}...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{backup_name}'!A2:B" # Skip header, read A and B
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No data found in backup.")
        return
    
    # 2. Prepare new format
    headers = ["Sign ID", "Latitude", "Longitude", "Status", "Right Arrow", "Left Arrow", "Fri_Sat", "Details"]
    new_rows = [headers]
    
    print(f"Parsing {len(rows)} signs and reformatting...")
    for row in rows:
        if len(row) < 2: continue
        
        sign_id = row[0]
        json_str = row[1]
        
        try:
            # If the backup was already partially reformatted, the json_str might not be json
            if json_str.startswith('{'):
                details = json.loads(json_str)
            else:
                # Handle cases where we might have accidentally overwritten backup with headers
                continue
            new_rows.append(parse_sign(sign_id, details))
        except json.JSONDecodeError:
            print(f"Error parsing JSON for {sign_id}")
            continue

    # 3. Update original sheet ('Status')
    print(f"Updating {original_sheet_name} with {len(new_rows)-1} signs...")
    
    # Clear all data first
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{original_sheet_name}'!A:Z"
    ).execute()
    
    # Write new data
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{original_sheet_name}'!A1",
        valueInputOption='RAW',
        body={'values': new_rows}
    ).execute()
    
    print("Reformatting complete! Data is now in separate columns.")

def parse_sign(sign_id, details):
    """Helper to convert sign JSON to a row list"""
    # ID format: sign-35.0546116--80.7221836
    lat = ""
    lng = ""
    if sign_id and sign_id.startswith("sign-"):
        parts = sign_id.replace("sign-", "").split("--")
        if len(parts) == 2:
            lat = parts[0]
            lng = parts[1]
            if not lng.startswith("-"):
                lng = "-" + lng

    return [
        sign_id,
        lat,
        lng,
        details.get('status', 'need'),
        details.get('right', 0),
        details.get('left', 0),
        details.get('fri_sat', 0),
        details.get('details', 0)
    ]

if __name__ == "__main__":
    reformat_spreadsheet()

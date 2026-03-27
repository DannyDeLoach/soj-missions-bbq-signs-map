import datetime
from googleapiclient.discovery import build
from my_library import get_google_credentials

# Configuration
SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI'

def reformat_spreadsheet():
    creds = get_google_credentials()
    if not creds:
        return
    
    service = build('sheets', 'v4', credentials=creds)
    
    # 1. Get the current sheet name (usually the first one)
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    original_sheet = spreadsheet['sheets'][0]['properties']
    original_sheet_name = original_sheet['title']
    original_sheet_id = original_sheet['sheetId']
    
    print(f"Original sheet: {original_sheet_name}")
    
    # 2. Create a backup tab (Duplicate)
    backup_name = f"Backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating backup tab: {backup_name}...")
    
    duplicate_request = {
        'duplicateSheet': {
            'sourceSheetId': original_sheet_id,
            'newSheetName': backup_name
        }
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [duplicate_request]}
    ).execute()
    
    # 3. Read the data from the original sheet
    print(f"Reading data from {original_sheet_name}...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{original_sheet_name}'!A:A"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No data found in original sheet.")
        return
    
    # 4. Prepare new format
    # Headers: Sign ID, Latitude, Longitude, Status, Right Arrow, Left Arrow, Fri_Sat, Details
    headers = ["Sign ID", "Latitude", "Longitude", "Status", "Right Arrow", "Left Arrow", "Fri_Sat", "Details"]
    new_rows = [headers]
    
    print("Parsing JSON data and reformatting...")
    for row in rows:
        if not row: continue
        import json
        try:
            # The current data seems to be stored as one JSON object per cell in column A
            # (Based on how doGet works in Apps Script for many of these setups)
            # Actually, looking at inspect_spreadsheet.py output, the Apps Script returns
            # {id: {details}}. It's possible the sheet has one JSON string per row or 
            # some other format. Let's see what's actually in row[0].
            
            data = json.loads(row[0])
            
            # If data is a dict (like the whole sheet state), we'll loop through it.
            # If it's just one sign, we'll process that.
            
            if isinstance(data, dict) and 'id' not in data:
                # This is likely the entire state object {id: {sign_data}}
                for sign_id, details in data.items():
                    new_rows.append(parse_sign(sign_id, details))
            else:
                # This is a single sign object
                new_rows.append(parse_sign(data.get('id'), data))
                
        except json.JSONDecodeError:
            print(f"Skipping non-JSON row: {row[0][:50]}...")
            continue

    # 5. Clear original sheet and write new data
    print(f"Updating {original_sheet_name} with new column format...")
    
    # Clear all data
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
    
    print("Reformatting complete!")

def parse_sign(sign_id, details):
    """Helper to convert sign JSON to a row list"""
    # ID format: sign-35.0546116--80.7221836
    # Latitude/Longitude extraction
    lat = ""
    lng = ""
    if sign_id and sign_id.startswith("sign-"):
        parts = sign_id.replace("sign-", "").split("--")
        if len(parts) == 2:
            lat = parts[0]
            lng = "-" + parts[1] if not parts[1].startswith("-") else parts[1]

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

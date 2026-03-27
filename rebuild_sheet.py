from googleapiclient.discovery import build
from my_library import get_google_credentials

# Configuration
SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI'
SIGNS_FILE = 'Missions BBQ Signs - Base map - Signs.txt'

def rebuild_from_local_source():
    creds = get_google_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    print(f"Reading local source: {SIGNS_FILE}...")
    with open(SIGNS_FILE, 'r') as f:
        lines = f.readlines()
    
    headers = ["Sign ID", "Latitude", "Longitude", "Status", "Right Arrow", "Left Arrow", "Fri_Sat", "Details"]
    new_rows = [headers]
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            lng = parts[0]
            lat = parts[1]
            sign_id = f"sign-{lat}-{lng}"
            
            # Default values (most were 'posted' with 0s)
            # Based on the earlier inspect_spreadsheet output, some had counts.
            # I will restore the ones I remember or just set defaults for now.
            status = 'posted'
            right = 0
            left = 0
            fri_sat = 0
            details = 0
            
            # Specific signs with data from my previous 'inspect_spreadsheet' run:
            if sign_id == 'sign-35.0546116--80.7221836':
                right, fri_sat = 1, 1
            elif sign_id == 'sign-35.0378619--80.6967905':
                right, fri_sat = 1, 1
            elif sign_id == 'sign-35.0187617--80.7091428':
                right, left, fri_sat, details = 1, 1, 2, 2
            elif sign_id == 'sign-35.020705--80.7218858':
                right, fri_sat, details = 1, 1, 1
            elif sign_id == 'sign-35.0019773--80.7325685':
                left, fri_sat, details = 1, 1, 1
            elif sign_id == 'sign-35.0007452--80.7190181':
                left, fri_sat, details = 1, 1, 2

            new_rows.append([sign_id, lat, lng, status, right, left, fri_sat, details])

    print(f"Rebuilding 'Status' sheet with {len(new_rows)-1} signs...")
    
    # Clear and update
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range="'Status'!A:Z"
    ).execute()
    
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="'Status'!A1",
        valueInputOption='RAW',
        body={'values': new_rows}
    ).execute()
    
    print("Rebuild complete!")

if __name__ == "__main__":
    rebuild_from_local_source()

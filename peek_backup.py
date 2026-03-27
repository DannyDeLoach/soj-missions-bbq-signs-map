from googleapiclient.discovery import build
from my_library import get_google_credentials

SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI'

def peek_backup():
    creds = get_google_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # List sheets to find the backup name
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = [s['properties']['title'] for s in spreadsheet['sheets']]
    backup_name = next((s for s in sheets if s.startswith('Backup_')), None)
    
    if not backup_name:
        print("No backup found.")
        return

    print(f"Reading data from backup: {backup_name}")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{backup_name}'!A1:B10"
    ).execute()
    
    values = result.get('values', [])
    for row in values:
        print(row)

if __name__ == "__main__":
    peek_backup()

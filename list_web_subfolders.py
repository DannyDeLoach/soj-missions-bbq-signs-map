# list_web_subfolders.py

import sys

# Add the library path if not already present
if 'D:\\Scripting\\__Python' not in sys.path:
    sys.path.append('D:\\Scripting\\__Python')

try:
    from my_library.credentials.credentials_nas import load_nas_auditor_credentials
    from synology_api import filestation
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

DSM_VERSION = 7
HTTPS_PORT = '5001'

def list_subfolders():
    creds = load_nas_auditor_credentials()
    user, password, ip = creds
    
    print(f"Connecting to NAS at {ip} as '{user}' to list subfolders in '/web'...")
    
    try:
        # Initialize FileStation API
        fs = filestation.FileStation(ip, HTTPS_PORT, user, password, secure=True, cert_verify=False, dsm_version=DSM_VERSION)

        # List contents of the 'web' shared folder
        # In FileStation API, shared folders are referenced as '/shared_folder_name'
        result = fs.get_file_list(folder_path='/web')
        
        if isinstance(result, dict) and "data" in result:
            files = result["data"].get("files", [])
            subfolders = [f.get("name") for f in files if f.get("is_dir")]
            
            print("\n" + "="*40)
            print("SUBFOLDERS IN '/web'")
            print("="*40)
            if subfolders:
                for folder in subfolders:
                    print(f"- {folder}")
            else:
                print("(No subfolders found)")
            print("="*40)
        else:
            print(f"Could not retrieve folder list. Result: {result}")

    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        if 'fs' in locals():
            try: fs.logout()
            except: pass

if __name__ == "__main__":
    list_subfolders()
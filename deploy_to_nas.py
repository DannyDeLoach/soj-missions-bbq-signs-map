# deploy_to_nas.py

import sys
import os

# Add the library path if not already present
if 'D:\\Scripting\\__Python' not in sys.path:
    sys.path.append('D:\\Scripting\\__Python')

try:
    from my_library.credentials.credentials_nas import load_nas_credentials
    from synology_api import filestation
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

DSM_VERSION = 7
HTTPS_PORT = '5001'
NAS_FOLDER = '/web/soj-missions-bbq-signs'
FILES_TO_UPLOAD = [
    'index.html',
    'Missions BBQ Signs - Base map - Signs.txt',
    'Missions BBQ Signs - Base map- Groups.csv',
    'Missions BBQ Signs - Base map- SOJ.txt'
]

def deploy():
    creds = load_nas_credentials()
    user, password, ip = creds
    
    print(f"Connecting to NAS at {ip} as '{user}' for deployment...")
    
    try:
        # Initialize FileStation API
        fs = filestation.FileStation(ip, HTTPS_PORT, user, password, secure=True, cert_verify=False, dsm_version=DSM_VERSION)

        # 1. Ensure the target folder exists
        print(f"Checking if {NAS_FOLDER} exists...")
        folder_list = fs.get_file_list(folder_path='/web')
        if isinstance(folder_list, dict) and "data" in folder_list:
            files = folder_list["data"].get("files", [])
            existing_subfolders = [f.get("name") for f in files if f.get("is_dir")]
            
            if 'soj-missions-bbq-signs' not in existing_subfolders:
                print(f"Creating folder: {NAS_FOLDER}")
                fs.create_folder('/web', 'soj-missions-bbq-signs')
            else:
                print("Folder exists.")

        # 2. Upload Files
        print("\nUploading files...")
        for filename in FILES_TO_UPLOAD:
            if os.path.exists(filename):
                print(f"- Uploading {filename}...")
                # The upload method takes (dest_path, file_path)
                result = fs.upload_file(NAS_FOLDER, filename)
                # Note: synology_api upload_file sometimes returns a string on success
                if isinstance(result, str) or (isinstance(result, dict) and result.get("success")):
                    print(f"  Success!")
                else:
                    print(f"  Upload response: {result}")
            else:
                print(f"- Warning: {filename} not found locally, skipping.")

        print(f"\n==============================================")
        print(f"DEPLOYMENT COMPLETE")
        print(f"Your map is live at: http://{ip}/soj-missions-bbq-signs/index.html")
        print(f"==============================================")

    except Exception as e:
        print(f"Critical error during deployment: {e}")
    finally:
        if 'fs' in locals():
            try: fs.logout()
            except: pass

if __name__ == "__main__":
    deploy()
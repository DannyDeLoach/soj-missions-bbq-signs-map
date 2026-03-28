# check_nas_setup.py

import sys

# Add the library path if not already present
if 'D:\\Scripting\\__Python' not in sys.path:
    sys.path.append('D:\\Scripting\\__Python')

try:
    from my_library.credentials.credentials_nas import load_nas_auditor_credentials
    from synology_api import core_sys_info
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

DSM_VERSION = 7
HTTPS_PORT = '5001'

def check_setup():
    creds = load_nas_auditor_credentials()
    user, password, ip = creds
    
    print(f"Connecting to NAS at {ip} as '{user}'...")
    
    setup_info = {
        "web_folder_exists": False,
        "web_station_installed": False,
        "shared_folders": []
    }

    try:
        common_args = (ip, HTTPS_PORT, user, password)
        common_kwargs = {"secure": True, "cert_verify": False, "dsm_version": DSM_VERSION}
        
        sys_info = core_sys_info.SysInfo(*common_args, **common_kwargs)

        # 1. Check Shared Folders
        print("- Checking Shared Folders...")
        folders_res = sys_info.shared_folders_info()
        if isinstance(folders_res, dict) and "data" in folders_res:
            shares = folders_res["data"].get("shares", [])
            setup_info["shared_folders"] = [s.get("name") for s in shares]
            if "web" in setup_info["shared_folders"]:
                setup_info["web_folder_exists"] = True

        # 2. Check Installed Packages
        print("- Checking Installed Packages...")
        # get_installed_packages() is a common method in SysInfo for DSM 7
        try:
            packages_res = sys_info.get_installed_packages()
            if isinstance(packages_res, dict) and "data" in packages_res:
                packages = packages_res["data"].get("packages", [])
                for pkg in packages:
                    if pkg.get("id") == "WebStation" or pkg.get("name") == "Web Station":
                        setup_info["web_station_installed"] = True
                        setup_info["web_station_status"] = pkg.get("status")
                        break
        except Exception as e:
            print(f"  (Note: Could not list packages directly: {e})")

        print("\n" + "="*40)
        print("NAS WEB HOSTING STATUS")
        print("="*40)
        print(f"Web Shared Folder:    {'FOUND' if setup_info['web_folder_exists'] else 'MISSING'}")
        
        if setup_info['web_station_installed']:
            print(f"Web Station Package:  INSTALLED ({setup_info.get('web_station_status', 'unknown')})")
        else:
            print("Web Station Package:  NOT FOUND (via SysInfo list)")
            
        print("="*40)
        
        if setup_info["web_folder_exists"]:
            print("\nSUCCESS: The 'web' folder exists. You can host your map here.")
        else:
            print("\nACTION REQUIRED: Please create a shared folder named 'web' or install 'Web Station'.")

    except Exception as e:
        print(f"Critical error during check: {e}")
    finally:
        if 'sys_info' in locals():
            try: sys_info.logout()
            except: pass

if __name__ == "__main__":
    check_setup()
# generate_nas_security_report.py

import json
import sys
import os
from datetime import datetime

# Add the library path if not already present
if 'D:\\Scripting\\__Python' not in sys.path:
    sys.path.append('D:\\Scripting\\__Python')

try:
    from my_library.credentials.credentials_nas import load_nas_auditor_credentials
except ImportError as e:
    print(f"Error importing credentials: {e}")
    sys.exit(1)

try:
    from synology_api import core_sys_info, core_user, security_advisor
except ImportError as e:
    print(f"Error importing synology-api: {e}")
    sys.exit(1)

# ==========================================
# MODULE-LEVEL CONSTANTS
# ==========================================
DSM_VERSION = 7
HTTPS_PORT = '5001'

def gather_security_data():
    creds = load_nas_auditor_credentials()
    user, password, ip = creds
    
    print(f"Connecting to NAS at {ip} as service account: '{user}'...")
    
    report = {
        "report_generated_at": datetime.now().isoformat(),
        "nas_ip": ip
    }

    try:
        common_args = (ip, HTTPS_PORT, user, password)
        common_kwargs = {"secure": True, "cert_verify": False, "dsm_version": DSM_VERSION}
        
        sys_info = core_sys_info.SysInfo(*common_args, **common_kwargs)
        user_api = core_user.User(*common_args, **common_kwargs)
        sec_advisor = security_advisor.SecurityAdvisor(*common_args, **common_kwargs)

        print("- Gathering System Info...")
        try:
            report["system_info"] = sys_info.get_system_info()
            report["dsm_info"] = sys_info.dsm_info()
            report["sys_status"] = sys_info.sys_status()
        except: pass
        
        print("- Gathering Security Scan Info...")
        try: report["security_scan_info"] = sys_info.get_security_scan_info()
        except: pass
        
        print("- Gathering User and Password Policies...")
        try:
            report["users"] = user_api.get_users()
            report["password_policy"] = user_api.get_password_policy()
        except: pass
        
        print("- Gathering Network Services Security...")
        try:
            report["terminal_info"] = sys_info.terminal_info() 
            report["firewall_info"] = sys_info.firewall_info()
        except: pass
        
        print("- Gathering Security Advisor Report...")
        report["security_advisor"] = {}
        try: report["security_advisor"]["checklist"] = sec_advisor.checklist()
        except: pass
        try: report["security_advisor"]["login_activity"] = sec_advisor.login_activity()
        except: pass

        print("- Gathering Shared Folder Info...")
        try: report["shared_folders"] = sys_info.shared_folders_info()
        except: pass

    except Exception as e:
        print(f"Critical error during API initialization: {e}")
    finally:
        if 'sys_info' in locals():
            try: sys_info.logout()
            except: pass

    return report

def save_report(report, filename):
    if not report: return
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"\nReport saved to {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Error saving report: {e}")

def print_summary(report):
    if not report: return
    
    print("\n" + "="*50)
    print("      NAS SECURITY REPORT SUMMARY")
    print("="*50)
    
    # 1. SSH Status
    terminal_res = report.get("terminal_info", {})
    terminal_data = terminal_res.get("data", {}) if isinstance(terminal_res, dict) else {}
    if terminal_data:
        ssh_enabled = terminal_data.get("enable_ssh", False)
        print(f"SSH Enabled:     {'YES (Warning)' if ssh_enabled else 'No (Good)'}")
    
    # 2. Password Policy (Improved Parser)
    pw_res = report.get("password_policy", {})
    pw_data = pw_res.get("data", {}) if isinstance(pw_res, dict) else {}
    if pw_data:
        # DSM 7 uses different keys for length and complexity
        min_len = pw_data.get("min_len") or pw_data.get("min_char_len", "N/A")
        complex_req = pw_data.get("must_include_complex") or pw_data.get("enable_complex", "N/A")
        print(f"Password Policy: Min Length: {min_len}, Complexity: {complex_req}")
    else:
        print("Password Policy: No policy data found.")
    
    # 3. Security Advisor (Check for empty list)
    checklist_res = report.get("security_advisor", {}).get("checklist", {})
    checklist = checklist_res.get("data", []) if isinstance(checklist_res, dict) else []
    
    if isinstance(checklist, list) and len(checklist) > 0:
        fails = sum(1 for i in checklist if isinstance(i, dict) and i.get("severity") == "fail")
        warns = sum(1 for i in checklist if isinstance(i, dict) and i.get("severity") == "warning")
        print(f"Security Alerts: {fails} Fails, {warns} Warnings")
    else:
        print("Security Alerts: No scan results. Please run a scan in DSM.")
    
    # 4. DSM Version
    dsm_res = report.get("dsm_info", {})
    dsm_data = dsm_res.get("data", {}) if isinstance(dsm_res, dict) else {}
    if dsm_data:
        print(f"DSM Version:     {dsm_data.get('version_string', 'N/A')}")
            
    print("="*50)

if __name__ == "__main__":
    report_data = gather_security_data()
    if report_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nas_security_report_{timestamp}.json"
        save_report(report_data, filename)
        print_summary(report_data)
import os
import re
import json
import sys
from datetime import datetime

# Problemli dosya desenleri
PROBLEMATIC_PATTERNS = {
    "master_info": r"(master\.info$|master-version.*\.info$)",
    "relay_bin": r"(mysql-relay.*|relay-log-.*\.info$)",
    "error_log": r"error\.log$",
    "aria_log": r"(aria_log\.[0-9]+|aria_log\.000[0-9]*)",
    "index_files": r"\.index$",
    "000001_files": r"\.000001$",
    "ib_logfile": r"ib_logfile[0-9]*",
    "dump_files": r"mysqld\.dmp$"
}

GROUP_NAMES = {
    "master_info": "Master Info Dosyaları",
    "relay_bin": "Relay Bin Dosyaları",
    "error_log": "Hata Log Dosyaları",
    "aria_log": "Aria Log Dosyaları",
    "index_files": "Index Dosyaları",
    "000001_files": "000001 Dosyaları",
    "ib_logfile": "InnoDB Log Dosyaları",
    "dump_files": "Dump Dosyaları"
}

def find_problematic_files(path):
    """Belirtilen dizindeki problemli dosyaları tespit eder."""
    problematic_files = []
    grouped_files = {key: [] for key in PROBLEMATIC_PATTERNS.keys()}

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            for group, pattern in PROBLEMATIC_PATTERNS.items():
                if re.search(pattern, file):
                    grouped_files[group].append({
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    })
                    problematic_files.append(file_path)
                    break

    return problematic_files, grouped_files

def delete_files(file_list):
    """Liste verilen dosyaları siler."""
    deleted_files = []
    for file_path in file_list:
        try:
            os.remove(file_path)
            deleted_files.append(file_path)
        except Exception as e:
            print(f"Hata oluştu: {file_path} - {str(e)}")

    return deleted_files

if __name__ == "__main__":
    current_path = os.getcwd()

    if not os.path.isdir(current_path):
        print(json.dumps({"success": False, "message": "Geçersiz dizin yolu"}))
        sys.exit(1)

    problematic_files, grouped_files = find_problematic_files(current_path)

    if problematic_files:
        deleted_files = delete_files(problematic_files)
        message = f"{len(deleted_files)} adet problemli dosya silindi."
    else:
        message = "Problemli dosya bulunamadı."

    result = {
        "success": True,
        "message": message,
        "groups": GROUP_NAMES,
        "files": grouped_files
    }

    print(json.dumps(result, indent=4, ensure_ascii=False)) 
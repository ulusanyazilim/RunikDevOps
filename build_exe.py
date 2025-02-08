import PyInstaller.__main__
import os

# Logs klasörünü oluştur
os.makedirs("logs", exist_ok=True)

# Tüm Python dosyalarını bul
python_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

# PyInstaller parametreleri
params = [
    'main.py',  # Ana dosya
    '--onefile',  # Tek exe dosyası oluştur
    '--noconsole',  # Konsol penceresi gösterme
    '--name=RunikDevOps',  # Exe dosyasının adı
    '--icon=icon.ico',  # İkon dosyası (varsa)
    '--hidden-import=tkinter',
    '--hidden-import=psutil',
    '--hidden-import=winreg',
    '--hidden-import=ctypes',
]

# Logs klasörü varsa ekle
if os.path.exists('logs'):
    params.append('--add-data=logs;logs')

# Tüm Python dosyalarını hidden-import olarak ekle
for file in python_files:
    module_name = os.path.splitext(file)[0].replace(os.sep, '.')
    if module_name.startswith('.\\'):
        module_name = module_name[2:]
    params.append(f'--hidden-import={module_name}')

# PyInstaller'ı çalıştır
PyInstaller.__main__.run(params)

print("Build işlemi tamamlandı!")

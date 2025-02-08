import tkinter as tk
from disk_optimizer_tab import DiskOptimizerTab
from environment_tab import EnvironmentTab
from wsl_tab import WSLTab
from gradle_tab import GradleTab
from vram_tab import VramTab
from java_tab import JavaTab
from docker_tab import DockerTab
from nodejs_tab import NodejsTab
from python_tab import PythonTab
from flutter_tab import FlutterTab
from vscode_tab import VSCodeTab
from xampp_tab import XamppTab
import logging
import ctypes
import sys
import os
from datetime import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        # Yönetici olarak yeniden başlat
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{sys.argv[0]}"', 
            None, 
            1
        )
        return True
    return False

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra Gelişmiş Sistem Optimizasyonu")
        self.root.geometry("900x800")
        
        # Loglama
        self.setup_logging()

        # Notebook (Tab Control) oluştur
        self.notebook = tk.ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sekmeleri oluştur
        self.disk_tab = DiskOptimizerTab(self.notebook)
        self.env_tab = EnvironmentTab(self.notebook)
        self.wsl_tab = WSLTab(self.notebook)
        self.gradle_tab = GradleTab(self.notebook)
        self.vram_tab = VramTab(self.notebook)
        self.java_tab = JavaTab(self.notebook)
        self.docker_tab = DockerTab(self.notebook)
        self.nodejs_tab = NodejsTab(self.notebook)
        self.python_tab = PythonTab(self.notebook)
        self.flutter_tab = FlutterTab(self.notebook)
        self.vscode_tab = VSCodeTab(self.notebook)
        self.xampp_tab = XamppTab(self.notebook)
        
        # Sekmeleri ekle
        self.notebook.add(self.disk_tab, text="Disk Optimizasyonu")
        self.notebook.add(self.env_tab, text="Environment")
        self.notebook.add(self.wsl_tab, text="WSL")
        self.notebook.add(self.gradle_tab, text="Gradle")
        self.notebook.add(self.vram_tab, text="VRAM Ayarları")
        self.notebook.add(self.java_tab, text="Java Yönetimi")
        self.notebook.add(self.docker_tab, text="Docker")
        self.notebook.add(self.nodejs_tab, text="Node.js")
        self.notebook.add(self.python_tab, text="Python")
        self.notebook.add(self.flutter_tab, text="Flutter/Android")
        self.notebook.add(self.vscode_tab, text="VS Code/Git")
        self.notebook.add(self.xampp_tab, text="XAMPP")

    def setup_logging(self):
        """Detaylı günlük kaydı oluştur"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def main():
    # Yönetici değilse ve yeniden başlatıldıysa
    if run_as_admin():
        return

    try:
        root = tk.Tk()
        app = MainApplication(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Uygulama hatası: {e}")
        if root:
            root.destroy()

if __name__ == "__main__":
    main() 

from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import logging
import shutil
import sys

class PythonTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Python Sürümleri
        versions_frame = ttk.LabelFrame(self, text="Python Sürümleri", padding="10")
        versions_frame.pack(fill=tk.X, pady=5)
        
        # Sürüm listesi
        columns = ("Sürüm", "Konum", "pip", "Durum")
        self.python_list = ttk.Treeview(versions_frame, columns=columns, show="headings")
        
        for col in columns:
            self.python_list.heading(col, text=col)
        
        self.python_list.pack(fill=tk.X, pady=5)
        
        # pip Paketleri
        packages_frame = ttk.LabelFrame(self, text="Yüklü pip Paketleri", padding="10")
        packages_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Paket listesi
        pkg_columns = ("Paket", "Sürüm", "Konum")
        self.package_list = ttk.Treeview(packages_frame, columns=pkg_columns, show="headings")
        
        for col in pkg_columns:
            self.package_list.heading(col, text=col)
        
        self.package_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Sürümleri Tara", 
                  command=self.scan_python).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Paketleri Listele", 
                  command=self.list_packages).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="pip Cache Temizle", 
                  command=self.clean_pip_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="__pycache__ Temizle", 
                  command=self.clean_pycache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kullanılmayan Sürümleri Kaldır", 
                  command=self.cleanup_python).pack(side=tk.LEFT, padx=5)

    def scan_python(self):
        """Python sürümlerini tara"""
        try:
            # Python kurulum dizinlerini tara
            python_paths = [
                r"C:\Python*",
                r"E:\Python*",
                os.path.expanduser("~\\AppData\\Local\\Programs\\Python*")
            ]
            
            # Listeyi temizle
            for item in self.python_list.get_children():
                self.python_list.delete(item)
            
            for path_pattern in python_paths:
                import glob
                for path in glob.glob(path_pattern):
                    if os.path.isdir(path):
                        try:
                            # Python sürüm bilgisini al
                            python_exe = os.path.join(path, "python.exe")
                            if os.path.exists(python_exe):
                                result = subprocess.run([python_exe, "--version"], 
                                                     capture_output=True, text=True)
                                version = result.stdout.strip()
                                
                                # pip sürüm bilgisini al
                                pip_exe = os.path.join(path, "Scripts", "pip.exe")
                                if os.path.exists(pip_exe):
                                    result = subprocess.run([pip_exe, "--version"], 
                                                         capture_output=True, text=True)
                                    pip_version = result.stdout.split()[1]
                                else:
                                    pip_version = "Yok"
                                
                                status = "✅ Aktif" if path in sys.executable else "⚪ Pasif"
                                
                                self.python_list.insert("", tk.END, values=(
                                    version,
                                    path,
                                    pip_version,
                                    status
                                ))
                        except:
                            continue
            
        except Exception as e:
            logging.error(f"Python tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def list_packages(self):
        """Yüklü pip paketlerini listele"""
        selected = self.python_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir Python sürümü seçin!")
            return
            
        try:
            python_path = self.python_list.item(selected[0])['values'][1]
            pip_exe = os.path.join(python_path, "Scripts", "pip.exe")
            
            if not os.path.exists(pip_exe):
                messagebox.showwarning("Uyarı", "Seçili sürümde pip bulunamadı!")
                return
            
            # Listeyi temizle
            for item in self.package_list.get_children():
                self.package_list.delete(item)
            
            # Paketleri listele
            result = subprocess.run([pip_exe, "list", "--format=json"], 
                                 capture_output=True, text=True)
            packages = json.loads(result.stdout)
            
            for pkg in packages:
                self.package_list.insert("", tk.END, values=(
                    pkg['name'],
                    pkg['version'],
                    pkg.get('location', '')
                ))
            
        except Exception as e:
            logging.error(f"Paket listeleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_pip_cache(self):
        """pip önbelleğini temizle"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], check=True)
            messagebox.showinfo("Başarılı", "pip önbelleği temizlendi!")
            
        except Exception as e:
            logging.error(f"pip temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_pycache(self):
        """__pycache__ dizinlerini temizle"""
        try:
            count = 0
            for root, dirs, files in os.walk(os.path.expanduser("~")):
                if "__pycache__" in dirs:
                    cache_dir = os.path.join(root, "__pycache__")
                    shutil.rmtree(cache_dir)
                    count += 1
            
            messagebox.showinfo("Başarılı", f"{count} adet __pycache__ dizini temizlendi!")
            
        except Exception as e:
            logging.error(f"pycache temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def cleanup_python(self):
        """Kullanılmayan Python sürümlerini kaldır"""
        if not messagebox.askyesno("Onay", 
            "Bu işlem aktif olmayan Python sürümlerini kaldıracak.\n"
            "Devam etmek istiyor musunuz?"):
            return
            
        try:
            for item in self.python_list.get_children():
                values = self.python_list.item(item)['values']
                if values[3] == "⚪ Pasif":
                    python_path = values[1]
                    try:
                        shutil.rmtree(python_path)
                    except:
                        continue
            
            messagebox.showinfo("Başarılı", "Kullanılmayan Python sürümleri kaldırıldı!")
            self.scan_python()
            
        except Exception as e:
            logging.error(f"Python temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
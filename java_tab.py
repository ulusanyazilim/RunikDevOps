from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import winreg
import logging
import shutil

class JavaTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Java Sürümleri Listesi
        versions_frame = ttk.LabelFrame(self, text="Yüklü Java Sürümleri", padding="10")
        versions_frame.pack(fill=tk.X, pady=5)
        
        # Java listesi
        columns = ("Sürüm", "Konum", "Bit", "Durum")
        self.java_list = ttk.Treeview(versions_frame, columns=columns, show="headings")
        
        for col in columns:
            self.java_list.heading(col, text=col)
        
        self.java_list.pack(fill=tk.X, pady=5)
        
        # Kontrol butonları
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Java Sürümlerini Tara", 
                  command=self.scan_java_versions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Sürümü Varsayılan Yap", 
                  command=self.set_default_java).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kullanılmayan Sürümleri Temizle", 
                  command=self.cleanup_java).pack(side=tk.LEFT, padx=5)

    def scan_java_versions(self):
        """Java sürümlerini tara"""
        try:
            # Listeyi temizle
            for item in self.java_list.get_children():
                self.java_list.delete(item)
            
            # Olası Java dizinleri
            java_paths = [
                "C:\\Program Files\\Java",
                "C:\\Program Files (x86)\\Java",
                "E:\\Program Files\\Java",
                os.path.expandvars("%JAVA_HOME%")
            ]
            
            # PATH'teki Java dizinlerini bul
            path_dirs = os.environ.get('PATH', '').split(';')
            for dir in path_dirs:
                if 'java' in dir.lower() and 'bin' in dir.lower():
                    parent = os.path.dirname(dir.rstrip('\\'))
                    if parent not in java_paths:
                        java_paths.append(parent)
            
            for base_path in java_paths:
                if os.path.exists(base_path):
                    # Alt dizinleri kontrol et
                    for dir in os.listdir(base_path):
                        java_dir = os.path.join(base_path, dir)
                        java_bin = os.path.join(java_dir, "bin", "java.exe")
                        
                        if os.path.exists(java_bin):
                            # Java sürümünü al
                            try:
                                result = subprocess.run([java_bin, '-version'], 
                                                     capture_output=True, 
                                                     text=True, 
                                                     stderr=subprocess.STDOUT)
                                version = result.stderr.split('\n')[0]
                            except:
                                version = "Bilinmiyor"
                            
                            # PATH'te var mı kontrol et
                            bin_dir = os.path.join(java_dir, "bin")
                            is_in_path = bin_dir.lower() in [p.lower() for p in path_dirs]
                            
                            # 32/64 bit kontrolü
                            is_64bit = "64-Bit" if "64-Bit" in version else "32-Bit"
                            
                            self.java_list.insert("", tk.END, values=(
                                version,
                                java_dir,
                                is_64bit,
                                "✅ Aktif" if is_in_path else "⚪ Pasif"
                            ))
            
        except Exception as e:
            logging.error(f"Java tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def set_default_java(self):
        """Seçili Java sürümünü varsayılan yap"""
        selected = self.java_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir Java sürümü seçin!")
            return
            
        try:
            java_path = self.java_list.item(selected[0])['values'][1]
            
            # JAVA_HOME değişkenini ayarla
            subprocess.run(['setx', 'JAVA_HOME', java_path])
            
            # PATH'e bin dizinini ekle
            bin_path = os.path.join(java_path, "bin")
            current_path = os.environ.get('PATH', '')
            
            if bin_path not in current_path:
                new_path = f"{bin_path};{current_path}"
                subprocess.run(['setx', 'PATH', new_path])
            
            messagebox.showinfo("Başarılı", f"Varsayılan Java sürümü ayarlandı:\n{java_path}")
            
        except Exception as e:
            logging.error(f"Java ayarlama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def cleanup_java(self):
        """Kullanılmayan Java sürümlerini temizle"""
        # Kullanıcıya sor
        if not messagebox.askyesno("Onay", 
            "Bu işlem PATH'te olmayan Java sürümlerini kaldıracak.\n"
            "Devam etmek istiyor musunuz?"):
            return
            
        try:
            for item in self.java_list.get_children():
                values = self.java_list.item(item)['values']
                if values[3] == "⚪ Pasif":
                    java_path = values[1]
                    try:
                        shutil.rmtree(java_path)
                    except:
                        continue
            
            messagebox.showinfo("Başarılı", "Kullanılmayan Java sürümleri temizlendi!")
            self.scan_java_versions()  # Listeyi güncelle
            
        except Exception as e:
            logging.error(f"Java temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
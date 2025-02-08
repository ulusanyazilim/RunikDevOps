from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import logging
import os

class VramTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pagefile Bölümü
        pagefile_frame = ttk.LabelFrame(self, text="Pagefile.sys (Sanal Bellek)", padding="10")
        pagefile_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pagefile_frame, 
                 text="RAM yetersiz kaldığında sanal bellek olarak kullanılır.",
                 wraplength=550).pack(anchor=tk.W, pady=5)
        
        # Pagefile boyut seçimi
        size_frame = ttk.Frame(pagefile_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        size_values = [0, 1, 2, 4, 8, 16, 32]
        self.pagefile_size = tk.StringVar(value="16")
        
        ttk.Label(size_frame, text="Boyut (GB):").pack(side=tk.LEFT)
        self.pagefile_combo = ttk.Combobox(size_frame, values=size_values, 
                                         textvariable=self.pagefile_size, width=5, 
                                         state="readonly")
        self.pagefile_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(size_frame, text="Uygula", 
                  command=self.apply_pagefile).pack(side=tk.LEFT, padx=5)

        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, pady=10)

        # Hiberfil Bölümü
        hiberfil_frame = ttk.LabelFrame(self, text="Hiberfil.sys (Hazırda Bekletme)", padding="10")
        hiberfil_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(hiberfil_frame, 
                 text="Hazırda bekletme modunda RAM içeriğini saklar.",
                 wraplength=550).pack(anchor=tk.W, pady=5)
        
        # Hiberfil boyut seçimi
        hsize_frame = ttk.Frame(hiberfil_frame)
        hsize_frame.pack(fill=tk.X, pady=5)
        
        self.hiberfil_size = tk.StringVar(value="16")
        
        ttk.Label(hsize_frame, text="Boyut (GB):").pack(side=tk.LEFT)
        self.hiberfil_combo = ttk.Combobox(hsize_frame, values=size_values, 
                                         textvariable=self.hiberfil_size, width=5, 
                                         state="readonly")
        self.hiberfil_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(hsize_frame, text="Uygula", 
                  command=self.apply_hiberfil).pack(side=tk.LEFT, padx=5)

        # Durum Bilgisi
        status_frame = ttk.LabelFrame(self, text="Durum", padding="5")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="Hazır")
        ttk.Label(status_frame, textvariable=self.status_var).pack(fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Yeniden başlatma butonu
        ttk.Button(self, text="Yeniden Başlat", 
                  command=self.restart_pc).pack(pady=10)

    def apply_pagefile(self):
        """Pagefile boyutunu ayarla"""
        try:
            size_gb = int(self.pagefile_size.get())
            size_mb = size_gb * 1024
            
            self.update_status("Pagefile ayarlanıyor...", 20)
            
            if size_gb == 0:
                cmd = 'wmic pagefileset delete'
            else:
                cmd = f'wmic pagefileset where name="C:\\\\pagefile.sys" set InitialSize={size_mb},MaximumSize={size_mb}'
            
            subprocess.run(cmd, shell=True, check=True)
            
            self.update_status("Pagefile ayarlandı!", 100)
            messagebox.showinfo("Başarılı", f"Pagefile boyutu {size_gb}GB olarak ayarlandı!")
        except Exception as e:
            logging.error(f"Pagefile hatası: {e}")
            messagebox.showerror("Hata", "Pagefile ayarlanırken bir hata oluştu!")

    def apply_hiberfil(self):
        """Hiberfil boyutunu ayarla"""
        try:
            size_gb = int(self.hiberfil_size.get())
            size_mb = size_gb * 1024
            
            self.update_status("Hiberfil ayarlanıyor...", 20)
            
            if size_gb == 0:
                # Hazırda bekletmeyi kapat
                subprocess.run(['powercfg.exe', '/hibernate', 'off'], 
                             shell=True, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Önce hazırda bekletmeyi aç
                subprocess.run(['powercfg.exe', '/hibernate', 'on'], 
                             shell=True, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Boyutu ayarla (Windows 10 ve üzeri için)
                subprocess.run(['powercfg.exe', '/hibernate', '/size', str(size_mb)], 
                             shell=True, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Alternatif komut (eski Windows sürümleri için)
                if size_gb <= 100:  # 100GB'dan büyük değerler için güvenlik kontrolü
                    percent = int((size_gb / self.get_ram_size()) * 100)
                    subprocess.run(['powercfg.exe', '/hibernate', '/size', str(percent)], 
                                 shell=True, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.update_status("Hiberfil ayarlandı!", 100)
            messagebox.showinfo("Başarılı", f"Hiberfil boyutu {size_gb}GB olarak ayarlandı!")
        except Exception as e:
            logging.error(f"Hiberfil hatası: {e}")
            messagebox.showerror("Hata", f"Hiberfil ayarlanırken bir hata oluştu!\nHata: {str(e)}")

    def get_ram_size(self):
        """Sistemdeki RAM miktarını GB cinsinden al"""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except:
            return 16  # Varsayılan değer

    def restart_pc(self):
        """Bilgisayarı yeniden başlat"""
        if messagebox.askyesno("Yeniden Başlat", 
                             "Değişikliklerin etkili olması için sistem yeniden başlatılacak.\n"
                             "Devam etmek istiyor musunuz?"):
            subprocess.run("shutdown /r /t 0", shell=True) 
from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import winreg
import logging
import shutil

class WSLTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # WSL Bilgileri
        info_frame = ttk.LabelFrame(self, text="WSL Bilgileri", padding="5")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Mevcut WSL konumu
        current_path = os.path.expandvars(r"%LOCALAPPDATA%\wsl")
        ttk.Label(info_frame, text=f"Mevcut Konum: {current_path}").pack(anchor=tk.W)
        
        # Taşıma Ayarları
        settings_frame = ttk.LabelFrame(self, text="Taşıma Ayarları", padding="5")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Hedef Dizin
        ttk.Label(settings_frame, text="Hedef Dizin:").pack(side=tk.LEFT, padx=5)
        self.target_path = tk.StringVar(value="D:\\WSL")
        ttk.Entry(settings_frame, textvariable=self.target_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text="Gözat", command=self.browse_target).pack(side=tk.LEFT, padx=5)
        
        # Durum Bilgisi
        status_frame = ttk.LabelFrame(self, text="Durum", padding="5")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Hazır")
        ttk.Label(status_frame, textvariable=self.status_var).pack(fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="WSL Dağıtımlarını Tara", 
                  command=self.scan_distributions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Taşımayı Başlat", 
                  command=self.move_wsl).pack(side=tk.LEFT, padx=5)

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path.set(path)

    def scan_distributions(self):
        try:
            vhdx_files = self.find_wsl_vhdx()
            if not vhdx_files:
                messagebox.showinfo("Bilgi", "WSL dağıtımı bulunamadı!")
                return
                
            message = "Bulunan WSL dağıtımları:\n\n"
            total_size = 0
            for vhdx in vhdx_files:
                size = os.path.getsize(vhdx) / (1024**3)  # GB cinsinden
                message += f"- {os.path.basename(vhdx)}: {size:.2f} GB\n"
                total_size += size
            message += f"\nToplam boyut: {total_size:.2f} GB"
            
            messagebox.showinfo("WSL Dağıtımları", message)
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def find_wsl_vhdx(self):
        base_path = os.path.expandvars(r"%LOCALAPPDATA%\wsl")
        vhdx_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".vhdx"):
                    vhdx_files.append(os.path.join(root, file))
        return vhdx_files

    def move_wsl(self):
        try:
            if not messagebox.askyesno("Onay", 
                "WSL dağıtımları taşınacak. Bu işlem biraz zaman alabilir.\n"
                "Devam etmek istiyor musunuz?"):
                return
                
            target = self.target_path.get()
            self.update_status("WSL dağıtımları kapatılıyor...", 10)
            subprocess.run(["wsl", "--shutdown"], shell=True)
            
            vhdx_files = self.find_wsl_vhdx()
            if not vhdx_files:
                messagebox.showwarning("Uyarı", "WSL VHDX dosyası bulunamadı!")
                return
            
            self.update_status("Dağıtımlar taşınıyor...", 30)
            os.makedirs(target, exist_ok=True)
            
            for i, vhdx in enumerate(vhdx_files, 1):
                progress = 30 + (i/len(vhdx_files) * 40)
                self.update_status(f"Taşınıyor: {os.path.basename(vhdx)}", progress)
                new_path = os.path.join(target, os.path.basename(vhdx))
                shutil.move(vhdx, new_path)
                
                distro_name = os.path.splitext(os.path.basename(vhdx))[0]
                subprocess.run(f"wsl --import {distro_name} {target} {new_path} --version 2", shell=True)
            
            self.update_status("Registry güncelleniyor...", 80)
            self.change_wsl_default_path(target)
            
            self.update_status("Taşıma tamamlandı!", 100)
            messagebox.showinfo("Başarılı", "WSL dağıtımları başarıyla taşındı!")
            
        except Exception as e:
            logging.error(f"WSL taşıma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def change_wsl_default_path(self, new_path):
        key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "BasePath", 0, winreg.REG_SZ, new_path)
        except Exception as e:
            raise Exception(f"Registry güncellenirken hata: {e}") 
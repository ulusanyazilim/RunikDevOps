from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import logging
import subprocess
import time

class GradleTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Gradle Bilgileri
        info_frame = ttk.LabelFrame(self, text="Gradle Bilgileri", padding="5")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Mevcut Gradle konumu
        current_path = os.path.expanduser("~") + "\\.gradle"
        ttk.Label(info_frame, text=f"Mevcut Konum: {current_path}").pack(anchor=tk.W)
        
        if os.path.exists(current_path):
            size = self.get_folder_size(current_path)
            ttk.Label(info_frame, text=f"Mevcut Boyut: {size:.2f} GB").pack(anchor=tk.W)
        
        # Taşıma Ayarları
        settings_frame = ttk.LabelFrame(self, text="Taşıma Ayarları", padding="5")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Hedef Dizin
        ttk.Label(settings_frame, text="Hedef Dizin:").pack(side=tk.LEFT, padx=5)
        self.target_path = tk.StringVar(value="D:\\.gradle")
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
        
        ttk.Button(button_frame, text="Gradle'ı Tara", 
                  command=self.scan_gradle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Taşımayı Başlat", 
                  command=self.move_gradle).pack(side=tk.LEFT, padx=5)

    def get_folder_size(self, path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size / (1024**3)  # GB cinsinden

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path.set(path)

    def scan_gradle(self):
        try:
            gradle_path = os.path.expanduser("~") + "\\.gradle"
            if not os.path.exists(gradle_path):
                messagebox.showinfo("Bilgi", "Gradle dizini bulunamadı!")
                return
                
            size = self.get_folder_size(gradle_path)
            message = f"Gradle dizini boyutu: {size:.2f} GB\n\n"
            
            # Alt dizinleri listele
            for item in os.listdir(gradle_path):
                item_path = os.path.join(gradle_path, item)
                if os.path.isdir(item_path):
                    item_size = self.get_folder_size(item_path)
                    message += f"- {item}: {item_size:.2f} GB\n"
            
            messagebox.showinfo("Gradle Bilgileri", message)
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def move_gradle(self):
        try:
            if not messagebox.askyesno("Onay", 
                "Gradle dizini taşınacak. Bu işlem biraz zaman alabilir.\n"
                "Devam etmek istiyor musunuz?"):
                return
                
            source = os.path.expanduser("~") + "\\.gradle"
            target = self.target_path.get()
            
            if not os.path.exists(source):
                messagebox.showwarning("Uyarı", "Gradle dizini bulunamadı!")
                return
            
            # İlgili işlemleri sonlandır
            self.update_status("İşlemler sonlandırılıyor...", 10)
            processes = ['java.exe', 'javaw.exe', 'gradle.exe']
            for proc in processes:
                subprocess.run(f'taskkill /F /IM {proc} /T', shell=True)
            time.sleep(2)
            
            # Taşıma işlemi
            self.update_status("Gradle dizini taşınıyor...", 30)
            os.makedirs(target, exist_ok=True)
            
            # Dosyaları taşı
            total_size = sum(f.stat().st_size for f in os.scandir(source) if f.is_file())
            copied_size = 0
            
            for item in os.listdir(source):
                source_path = os.path.join(source, item)
                target_path = os.path.join(target, item)
                
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, target_path)
                    copied_size += os.path.getsize(source_path)
                else:
                    shutil.copytree(source_path, target_path)
                
                progress = 30 + (copied_size / total_size * 40)
                self.update_status(f"Taşınıyor: {item}", progress)
            
            # Eski dizini sil
            self.update_status("Eski dizin temizleniyor...", 80)
            shutil.rmtree(source)
            
            # Environment değişkenini güncelle
            self.update_status("Environment değişkeni güncelleniyor...", 90)
            subprocess.run(['setx', 'GRADLE_USER_HOME', target])
            
            self.update_status("Taşıma tamamlandı!", 100)
            messagebox.showinfo("Başarılı", "Gradle dizini başarıyla taşındı!")
            
        except Exception as e:
            logging.error(f"Gradle taşıma hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import logging
import subprocess
from threading import Thread
import psutil

class DiskOptimizerTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Disk Bilgileri
        info_frame = ttk.LabelFrame(self, text="Disk Bilgileri", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Disk listesi
        self.disk_list = ttk.Treeview(info_frame, columns=("Sürücü", "Toplam", "Kullanılan", "Boş", "Kullanım"), 
                                     show="headings")
        
        self.disk_list.heading("Sürücü", text="Sürücü")
        self.disk_list.heading("Toplam", text="Toplam")
        self.disk_list.heading("Kullanılan", text="Kullanılan")
        self.disk_list.heading("Boş", text="Boş")
        self.disk_list.heading("Kullanım", text="Kullanım %")
        
        self.disk_list.column("Sürücü", width=70)
        self.disk_list.column("Toplam", width=100)
        self.disk_list.column("Kullanılan", width=100)
        self.disk_list.column("Boş", width=100)
        self.disk_list.column("Kullanım", width=100)
        
        self.disk_list.pack(fill=tk.X, pady=5)
        
        # Temizlik Seçenekleri
        cleanup_frame = ttk.LabelFrame(self, text="Temizlik Seçenekleri", padding="10")
        cleanup_frame.pack(fill=tk.X, pady=5)
        
        # Seçenekler
        self.cleanup_options = {
            "temp": tk.BooleanVar(value=True),
            "windows_temp": tk.BooleanVar(value=True),
            "recycle_bin": tk.BooleanVar(value=True),
            "downloads": tk.BooleanVar(value=False),
            "prefetch": tk.BooleanVar(value=True)
        }
        
        ttk.Checkbutton(cleanup_frame, text="Temp Klasörü", 
                       variable=self.cleanup_options["temp"]).pack(anchor=tk.W)
        ttk.Checkbutton(cleanup_frame, text="Windows Temp", 
                       variable=self.cleanup_options["windows_temp"]).pack(anchor=tk.W)
        ttk.Checkbutton(cleanup_frame, text="Geri Dönüşüm Kutusu", 
                       variable=self.cleanup_options["recycle_bin"]).pack(anchor=tk.W)
        ttk.Checkbutton(cleanup_frame, text="Downloads Klasörü", 
                       variable=self.cleanup_options["downloads"]).pack(anchor=tk.W)
        ttk.Checkbutton(cleanup_frame, text="Prefetch Klasörü", 
                       variable=self.cleanup_options["prefetch"]).pack(anchor=tk.W)

        # Durum Bilgisi
        status_frame = ttk.LabelFrame(self, text="Durum", padding="5")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Hazır")
        ttk.Label(status_frame, textvariable=self.status_var).pack(fill=tk.X)
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Diskleri Tara", 
                  command=self.scan_disks).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Temizliği Başlat", 
                  command=self.start_cleanup).pack(side=tk.LEFT, padx=5)
        
        # İlk taramayı yap
        self.scan_disks()

    def scan_disks(self):
        """Diskleri tara ve bilgileri göster"""
        try:
            # Listeyi temizle
            for item in self.disk_list.get_children():
                self.disk_list.delete(item)
            
            # Diskleri tara
            for partition in psutil.disk_partitions():
                if os.name == 'nt' and 'cdrom' in partition.opts or partition.fstype == '':
                    continue
                
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Boyutları GB'a çevir
                total = usage.total / (1024**3)
                used = usage.used / (1024**3)
                free = usage.free / (1024**3)
                
                self.disk_list.insert("", tk.END, values=(
                    partition.mountpoint,
                    f"{total:.1f} GB",
                    f"{used:.1f} GB",
                    f"{free:.1f} GB",
                    f"{usage.percent}%"
                ))
            
            self.update_status("Disk taraması tamamlandı", 100)
            
        except Exception as e:
            logging.error(f"Disk tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def start_cleanup(self):
        """Temizlik işlemini başlat"""
        if not messagebox.askyesno("Onay", "Seçili öğeler silinecek. Devam etmek istiyor musunuz?"):
            return
        
        # Temizlik işlemini ayrı thread'de başlat
        Thread(target=self.cleanup_thread, daemon=True).start()

    def cleanup_thread(self):
        """Temizlik işlemini gerçekleştir"""
        try:
            self.update_status("Temizlik başlıyor...", 0)
            
            # Temp klasörü
            if self.cleanup_options["temp"].get():
                self.update_status("Temp klasörü temizleniyor...", 20)
                self.clean_folder(os.path.expandvars(r"%TEMP%"))
            
            # Windows Temp
            if self.cleanup_options["windows_temp"].get():
                self.update_status("Windows Temp temizleniyor...", 40)
                self.clean_folder(r"C:\Windows\Temp")
            
            # Geri Dönüşüm
            if self.cleanup_options["recycle_bin"].get():
                self.update_status("Geri dönüşüm kutusu temizleniyor...", 60)
                subprocess.run("rd /s /q C:\$Recycle.Bin", shell=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Downloads
            if self.cleanup_options["downloads"].get():
                self.update_status("Downloads klasörü temizleniyor...", 80)
                downloads = os.path.expanduser("~\\Downloads")
                self.clean_folder(downloads)
            
            # Prefetch
            if self.cleanup_options["prefetch"].get():
                self.update_status("Prefetch temizleniyor...", 90)
                self.clean_folder(r"C:\Windows\Prefetch")
            
            self.update_status("Temizlik tamamlandı!", 100)
            messagebox.showinfo("Başarılı", "Temizlik işlemi tamamlandı!")
            
            # Diskleri yeniden tara
            self.scan_disks()
            
        except Exception as e:
            logging.error(f"Temizlik hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_folder(self, folder):
        """Klasör içeriğini temizle"""
        try:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except:
                    continue
        except:
            pass 
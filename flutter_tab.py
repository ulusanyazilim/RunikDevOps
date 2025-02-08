from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import logging
import shutil
import json

class FlutterTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ana Frame (Scrollable)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve Scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Flutter Bilgileri
        info_frame = ttk.LabelFrame(scrollable_frame, text="Flutter Bilgileri", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.flutter_info = ttk.Label(info_frame, text="Flutter bilgileri yükleniyor...")
        self.flutter_info.pack(anchor=tk.W, pady=5)
        
        # Android SDK Bilgileri
        sdk_frame = ttk.LabelFrame(scrollable_frame, text="Android SDK Bilgileri", padding="10")
        sdk_frame.pack(fill=tk.X, pady=5)
        
        # SDK bileşenleri listesi
        columns = ("Paket", "Sürüm", "Konum", "Durum")
        self.sdk_list = ttk.Treeview(sdk_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.sdk_list.heading(col, text=col)
        
        self.sdk_list.pack(fill=tk.X, pady=5)
        
        # Önbellek Bilgileri
        cache_frame = ttk.LabelFrame(scrollable_frame, text="Önbellek Bilgileri", padding="10")
        cache_frame.pack(fill=tk.X, pady=5)
        
        self.cache_info = ttk.Label(cache_frame, text="Önbellek bilgileri yükleniyor...")
        self.cache_info.pack(anchor=tk.W, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Flutter Doktor", 
                  command=self.flutter_doctor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="SDK Bileşenlerini Tara", 
                  command=self.scan_sdk).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pub Cache Temizle", 
                  command=self.clean_pub_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Gradle Cache Temizle", 
                  command=self.clean_gradle_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Android Build Temizle", 
                  command=self.clean_android_builds).pack(side=tk.LEFT, padx=5)
        
        # Canvas ve Scrollbar'ı yerleştir
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # İlk taramayı yap
        self.flutter_doctor()
        self.scan_sdk()

    def flutter_doctor(self):
        """Flutter durumunu kontrol et"""
        try:
            # Flutter yolunu bul
            flutter_paths = [
                os.path.expanduser("~\\flutter\\bin\\flutter.bat"),
                "E:\\Program Files\\flutter\\bin\\flutter.bat",
                os.path.join(os.environ.get('FLUTTER_ROOT', ''), 'bin', 'flutter.bat')
            ]
            
            flutter_path = None
            for path in flutter_paths:
                if os.path.exists(path):
                    flutter_path = path
                    break
            
            if not flutter_path:
                raise Exception("Flutter bulunamadı!")
            
            result = subprocess.run([flutter_path, 'doctor', '-v'], 
                                 capture_output=True, text=True)
            self.flutter_info.config(text=result.stdout)
            
        except Exception as e:
            logging.error(f"Flutter doctor hatası: {e}")
            self.flutter_info.config(text=f"Flutter bilgileri alınamadı!\nHata: {str(e)}")

    def scan_sdk(self):
        """Android SDK bileşenlerini tara"""
        try:
            # Android SDK yolunu bul
            sdk_paths = [
                os.environ.get('ANDROID_HOME', ''),
                os.environ.get('ANDROID_SDK_ROOT', ''),
                "E:\\AndroidSdk",
                os.path.expanduser("~\\AppData\\Local\\Android\\Sdk")
            ]
            
            android_home = None
            for path in sdk_paths:
                if path and os.path.exists(path):
                    android_home = path
                    break
            
            if not android_home:
                raise Exception("Android SDK bulunamadı!")
            
            # sdkmanager yolunu bul
            sdkmanager_paths = [
                os.path.join(android_home, "cmdline-tools", "latest", "bin", "sdkmanager.bat"),
                os.path.join(android_home, "tools", "bin", "sdkmanager.bat")
            ]
            
            sdkmanager = None
            for path in sdkmanager_paths:
                if os.path.exists(path):
                    sdkmanager = path
                    break
            
            if not sdkmanager:
                raise Exception("sdkmanager bulunamadı!")
            
            # Listeyi temizle
            for item in self.sdk_list.get_children():
                self.sdk_list.delete(item)
            
            # Paketleri listele
            result = subprocess.run([sdkmanager, '--list', '--verbose'], 
                                 capture_output=True, text=True)
            
            # Çıktıyı parse et
            lines = result.stdout.split('\n')
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        package = parts[0].strip()
                        version = parts[1].strip()
                        location = parts[2].strip()
                        status = "✅ Yüklü" if "installed" in line.lower() else "⚪ Mevcut"
                        
                        self.sdk_list.insert("", tk.END, values=(
                            package, version, location, status
                        ))
            
            # Önbellek boyutlarını hesapla
            gradle_cache = os.path.expanduser("~\\.gradle")
            android_cache = os.path.join(android_home, "cache")
            
            gradle_size = self.get_folder_size(gradle_cache) if os.path.exists(gradle_cache) else 0
            android_size = self.get_folder_size(android_cache) if os.path.exists(android_cache) else 0
            
            cache_text = f"Gradle Önbellek: {gradle_size/1024/1024:.1f} MB\n"
            cache_text += f"Android SDK Önbellek: {android_size/1024/1024:.1f} MB"
            self.cache_info.config(text=cache_text)
            
        except Exception as e:
            logging.error(f"SDK tarama hatası: {e}")
            self.cache_info.config(text=f"SDK bilgileri alınamadı!\nHata: {str(e)}")

    def get_folder_size(self, path):
        """Klasör boyutunu hesapla"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def clean_pub_cache(self):
        """Flutter pub önbelleğini temizle"""
        try:
            # Flutter yolunu bul
            flutter_paths = [
                os.path.expanduser("~\\flutter\\bin\\flutter.bat"),
                "E:\\Program Files\\flutter\\bin\\flutter.bat",
                os.path.join(os.environ.get('FLUTTER_ROOT', ''), 'bin', 'flutter.bat')
            ]
            
            flutter_path = None
            for path in flutter_paths:
                if os.path.exists(path):
                    flutter_path = path
                    break
            
            if not flutter_path:
                raise Exception("Flutter bulunamadı!")
            
            subprocess.run([flutter_path, 'pub', 'cache', 'clean'], check=True)
            messagebox.showinfo("Başarılı", "Pub önbelleği temizlendi!")
            
        except Exception as e:
            logging.error(f"Pub temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_gradle_cache(self):
        """Gradle önbelleğini temizle"""
        try:
            gradle_cache = os.path.expanduser("~\\.gradle\\caches")
            if os.path.exists(gradle_cache):
                shutil.rmtree(gradle_cache)
                messagebox.showinfo("Başarılı", "Gradle önbelleği temizlendi!")
            
        except Exception as e:
            logging.error(f"Gradle temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_android_builds(self):
        """Android build klasörlerini temizle"""
        try:
            count = 0
            # Flutter projeleri için build klasörlerini temizle
            for root, dirs, files in os.walk(os.path.expanduser("~")):
                if "build" in dirs and "android" in dirs:
                    build_dir = os.path.join(root, "build")
                    if os.path.exists(build_dir):
                        shutil.rmtree(build_dir)
                        count += 1
            
            messagebox.showinfo("Başarılı", f"{count} adet build klasörü temizlendi!")
            
        except Exception as e:
            logging.error(f"Build temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
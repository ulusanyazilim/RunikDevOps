from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import logging
import winreg
from datetime import datetime
import time
import ctypes

class EnvironmentTab(BaseTab):
    PROTECTED_ENV_VARS = [
        # Geliştirme Ortamları
        "JAVA_HOME", "MAVEN_HOME", "GRADLE_HOME", 
        "ANDROID_HOME", "ANDROID_SDK_ROOT",
        "NODE_HOME", "NPM_HOME", "YARN_CACHE_FOLDER",
        "PYTHON_HOME", "PYTHONPATH",
        "GOROOT", "GOPATH",
        
        # IDE ve Araç Ortam Değişkenleri
        "IDEA_HOME", "RIDER_HOME", "PYCHARM_HOME",
        "VSCODE_HOME", "ECLIPSE_HOME",
        
        # Sistem Değişkenleri
        "PATH", "TEMP", "TMP", "SystemRoot",
        "ProgramFiles", "ProgramFiles(x86)", 
        "CommonProgramFiles", "CommonProgramFiles(x86)",
        "APPDATA", "LOCALAPPDATA", "USERPROFILE"
    ]

    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Environment Tablo Frame'i
        table_frame = ttk.LabelFrame(self, text="Environment Değişkenleri", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tablo oluştur
        columns = ("Değişken", "Değer", "Durum", "Seç")
        self.env_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Sütun başlıkları ve genişlikleri
        widths = {
            "Değişken": 100,
            "Değer": 400,
            "Durum": 150,
            "Seç": 50
        }
        for col in columns:
            self.env_table.heading(col, text=col)
            self.env_table.column(col, width=widths[col])
        
        # Tıklama olayını ekle
        self.env_table.bind('<Button-1>', self.on_click)
        
        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.env_table.yview)
        self.env_table.configure(yscrollcommand=scrollbar.set)
        
        # Tablo ve scrollbar'ı yerleştir
        self.env_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        
        # Tarama ve Seçim Butonları
        ttk.Button(button_frame, text="Environment'ları Tara", 
                  command=self.scan_environments).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Geçersiz Yolları İşaretle", 
                  command=self.select_invalid_paths).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Tekrarlı Yolları İşaretle", 
                  command=self.select_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Tümünü İşaretle", 
                  command=self.select_all_envs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İşaretleri Kaldır", 
                  command=self.clear_selections).pack(side=tk.LEFT, padx=5)
        
        # İşlem Butonları
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)
        
        ttk.Button(action_frame, text="İşaretli Yolları Sil", 
                  command=self.remove_selected_paths).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="İşaretlileri Yedekle", 
                  command=self.backup_selected_envs).pack(side=tk.LEFT, padx=5)

        # PATH Ekleme Bölümü
        add_frame = ttk.LabelFrame(self, text="PATH'e Program Ekle", padding="10")
        add_frame.pack(fill=tk.X, pady=5)
        
        # Program Seçimi
        program_frame = ttk.Frame(add_frame)
        program_frame.pack(fill=tk.X, pady=5)
        
        self.program_var = tk.StringVar()
        programs = [
            "Flutter SDK",
            "Node.js",
            "Python",
            "Java JDK",
            "Android SDK",
            "Git",
            "VS Code",
            "Özel Dizin..."
        ]
        
        ttk.Label(program_frame, text="Program:").pack(side=tk.LEFT, padx=5)
        self.program_combo = ttk.Combobox(program_frame, values=programs, 
                                        textvariable=self.program_var, state="readonly", width=30)
        self.program_combo.pack(side=tk.LEFT, padx=5)
        
        # Dizin Seçimi
        path_frame = ttk.Frame(add_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Dizin:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(path_frame, text="Gözat", 
                  command=self.browse_program_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="PATH'e Ekle", 
                  command=self.add_to_path).pack(side=tk.LEFT, padx=5)
        
        # Program değiştiğinde dizin önerisi
        self.program_combo.bind('<<ComboboxSelected>>', self.suggest_program_path)

    def scan_environments(self):
        """Environment değişkenlerini tara ve tabloya ekle"""
        try:
            # Tabloyu temizle
            for item in self.env_table.get_children():
                self.env_table.delete(item)
            
            self.update_status("Environment değişkenleri taranıyor...", 0)
            
            # Environment değişkenlerini kontrol et
            total = len(self.PROTECTED_ENV_VARS)
            for i, var in enumerate(self.PROTECTED_ENV_VARS, 1):
                value = os.environ.get(var, '')
                if value:
                    if var == "PATH":
                        # PATH değişkenini özel olarak işle
                        self.analyze_path_variable(value)
                    else:
                        # Diğer değişkenler için normal kontrol
                        exists = os.path.exists(value) if os.path.isabs(value) else True
                        status = "✅ Geçerli" if exists else "❌ Dizin Bulunamadı"
                        self.env_table.insert("", tk.END, values=(var, value, status, ""))
                
                progress = (i / total) * 100
                self.update_status(f"Taranan: {var}", progress)
            
            self.update_status("Tarama tamamlandı!", 100)
            
        except Exception as e:
            logging.error(f"Environment tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def analyze_path_variable(self, path_value):
        """PATH değişkenini analiz et"""
        paths = path_value.split(';')
        for i, path in enumerate(paths):
            if path:  # Boş path'leri atla
                exists = os.path.exists(path) if os.path.isabs(path) else True
                status = "✅ Geçerli" if exists else "❌ Dizin Bulunamadı"
                self.env_table.insert("", tk.END, 
                    values=(f"PATH[{i+1}]", path, status, ""))

    def select_all_envs(self):
        """Tüm environment değişkenlerini seç"""
        for item in self.env_table.get_children():
            self.env_table.set(item, "Seç", "✓")

    def on_click(self, event):
        """Tablo hücresine tıklandığında checkbox davranışı"""
        region = self.env_table.identify_region(event.x, event.y)
        if region == "cell":
            column = self.env_table.identify_column(event.x)
            if str(column) == "#4":  # Seç kolonuna tıklandıysa
                item = self.env_table.identify_row(event.y)
                current_value = self.env_table.set(item, "Seç")
                # Checkbox gibi toggle yap
                new_value = "" if current_value == "✓" else "✓"
                self.env_table.set(item, "Seç", new_value)

    def select_duplicates(self):
        """Tekrarlı PATH değişkenlerini seç"""
        paths = {}  # {path: [item_ids]}
        
        # Önce tüm PATH değişkenlerini topla
        for item in self.env_table.get_children():
            var = self.env_table.set(item, "Değişken")
            if var.startswith("PATH["):
                path = self.env_table.set(item, "Değer").lower()  # Case-insensitive karşılaştırma
                if path:
                    paths.setdefault(path, []).append(item)
        
        # Tekrarlı olanları seç
        for path, items in paths.items():
            if len(items) > 1:
                # İlki hariç hepsini seç
                for item in items[1:]:
                    self.env_table.set(item, "Seç", "✓")
        
        messagebox.showinfo("Bilgi", "Tekrarlı PATH değişkenleri seçildi!")

    def select_invalid_paths(self):
        """Geçersiz PATH değişkenlerini seç"""
        count = 0
        for item in self.env_table.get_children():
            var = self.env_table.set(item, "Değişken")
            if var.startswith("PATH["):
                status = self.env_table.set(item, "Durum")
                if status == "❌ Dizin Bulunamadı":
                    self.env_table.set(item, "Seç", "✓")
                    count += 1
        
        messagebox.showinfo("Bilgi", f"{count} geçersiz PATH değişkeni seçildi!")

    def clear_selections(self):
        """Tüm işaretleri kaldır"""
        for item in self.env_table.get_children():
            self.env_table.set(item, "Seç", "")
        self.update_status("Tüm işaretler kaldırıldı", 100)

    def get_system_path(self):
        """Sistem PATH değişkenini al"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, 
                winreg.KEY_READ) as key:
                return winreg.QueryValueEx(key, 'Path')[0]
        except Exception as e:
            logging.error(f"Sistem PATH okuma hatası: {e}")
            return ""

    def get_user_path(self):
        """Kullanıcı PATH değişkenini al"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                'Environment', 0, winreg.KEY_READ) as key:
                return winreg.QueryValueEx(key, 'Path')[0]
        except Exception as e:
            logging.error(f"Kullanıcı PATH okuma hatası: {e}")
            return ""

    def set_system_path(self, new_path):
        """Sistem PATH değişkenini güncelle"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, 
                winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            return True
        except Exception as e:
            logging.error(f"Sistem PATH yazma hatası: {e}")
            return False

    def set_user_path(self, new_path):
        """Kullanıcı PATH değişkenini güncelle"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                'Environment', 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            return True
        except Exception as e:
            logging.error(f"Kullanıcı PATH yazma hatası: {e}")
            return False

    def remove_selected_paths(self):
        """İşaretli PATH konumlarını sil"""
        try:
            selected = []
            path_items = []  # PATH için seçilen öğeleri ayrı topla
            
            for item in self.env_table.get_children():
                if self.env_table.set(item, "Seç") == "✓":
                    var = self.env_table.set(item, "Değişken")
                    value = self.env_table.set(item, "Değer")
                    
                    if var.startswith("PATH["):
                        path_items.append(value.strip())  # Boşlukları temizle
                    else:
                        selected.append(var)
            
            if not (selected or path_items):
                return
                
            message = ""
            if selected:
                message += f"{len(selected)} environment değişkeni silinecek.\n"
            if path_items:
                message += f"{len(path_items)} PATH konumu silinecek.\n"
                
            if messagebox.askyesno("Onay", message + "Devam etmek istiyor musunuz?"):
                self.update_status("İşlem başlıyor...", 0)
                
                # Yedekleme işlemleri...
                backup_dir = "backups"
                os.makedirs(backup_dir, exist_ok=True)
                backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Mevcut değerleri yedekle
                current_system_path = self.get_system_path()
                current_user_path = self.get_user_path()
                
                with open(os.path.join(backup_dir, f"system_path_{backup_time}.txt"), 'w', encoding='utf-8') as f:
                    f.write(current_system_path)
                with open(os.path.join(backup_dir, f"user_path_{backup_time}.txt"), 'w', encoding='utf-8') as f:
                    f.write(current_user_path)
                
                self.update_status("Yedekleme tamamlandı", 20)
                
                try:
                    # PATH güncellemeleri
                    if path_items:
                        # Sistem PATH'ini güncelle
                        if current_system_path:
                            new_system_paths = []
                            for p in current_system_path.split(';'):
                                p = p.strip()
                                if p and p not in path_items and p.lower() not in [x.lower() for x in new_system_paths]:
                                    new_system_paths.append(p)
                            
                            new_system_path = ';'.join(new_system_paths)
                            self.set_system_path(new_system_path)
                        
                        # Kullanıcı PATH'ini güncelle
                        if current_user_path:
                            new_user_paths = []
                            for p in current_user_path.split(';'):
                                p = p.strip()
                                if p and p not in path_items and p.lower() not in [x.lower() for x in new_user_paths]:
                                    new_user_paths.append(p)
                            
                            new_user_path = ';'.join(new_user_paths)
                            self.set_user_path(new_user_path)
                        
                        # Değişiklikleri bildir
                        import win32con
                        import win32gui
                        win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
                        
                        self.update_status("PATH değişkenleri güncellendi", 80)
                        
                    # Normal değişkenleri sil
                    for var in selected:
                        subprocess.run(['setx', var, ''], capture_output=True)
                        
                    self.update_status("İşlem tamamlandı!", 100)
                    messagebox.showinfo("Başarılı", "Değişiklikler uygulandı!")
                    
                    # Tabloyu yenile
                    self.scan_environments()
                    
                except Exception as e:
                    logging.error(f"PATH güncelleme hatası: {e}")
                    messagebox.showerror("Hata", f"PATH güncellenirken hata oluştu: {e}")
                
        except Exception as e:
            logging.error(f"Silme işlemi hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def backup_selected_envs(self):
        """Seçili environment değişkenlerini yedekle"""
        selected = []
        for item in self.env_table.get_children():
            if self.env_table.set(item, "Seç") == "✓":
                var = self.env_table.set(item, "Değişken")
                value = self.env_table.set(item, "Değer")
                selected.append((var, value))
        
        if selected:
            try:
                # Yedek dosyası için dizin oluştur
                backup_dir = "backups"
                os.makedirs(backup_dir, exist_ok=True)
                
                # Yedek dosyası oluştur
                backup_file = os.path.join(backup_dir, 
                    f"env_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg")
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write("Windows Registry Editor Version 5.00\n\n")
                    f.write("[HKEY_CURRENT_USER\\Environment]\n")
                    for var, value in selected:
                        f.write(f'"{var}"="{value}"\n')
                
                messagebox.showinfo("Başarılı", 
                    f"Seçili değişkenler yedeklendi:\n{backup_file}")
                
            except Exception as e:
                logging.error(f"Yedekleme hatası: {e}")
                messagebox.showerror("Hata", str(e))

    def browse_program_path(self):
        """Program dizini seç"""
        program = self.program_var.get()
        
        # Program türüne göre başlangıç dizini öner
        initial_dirs = {
            "Flutter SDK": ["E:\\Program Files\\flutter", "C:\\flutter"],
            "Node.js": ["E:\\Program Files\\nodejs", "C:\\Program Files\\nodejs"],
            "Python": ["E:\\Python310", "C:\\Python310"],
            "Java JDK": ["E:\\Program Files\\Java", "C:\\Program Files\\Java"],
            "Android SDK": ["E:\\AndroidSdk", "C:\\Users\\%USERNAME%\\AppData\\Local\\Android\\Sdk"],
            "Git": ["E:\\Program Files\\Git", "C:\\Program Files\\Git"],
            "VS Code": ["E:\\Program Files\\Microsoft VS Code", "C:\\Program Files\\Microsoft VS Code"]
        }
        
        initial = "C:\\"
        if program in initial_dirs:
            for dir in initial_dirs[program]:
                expanded = os.path.expandvars(dir)
                if os.path.exists(expanded):
                    initial = expanded
                    break
        
        # Dizin seçiciyi başlat
        path = filedialog.askdirectory(
            initialdir=initial, 
            title=f"{program} Dizinini Seç"
        )
        
        if path:
            # Seçilen yolu Windows formatına çevir
            path = os.path.normpath(path)
            
            # Program türüne göre özel kontroller
            if program == "Flutter SDK":
                # Flutter için bin klasörünü kontrol et
                if not path.endswith('\\bin'):
                    bin_path = os.path.join(path, "bin")
                    if os.path.exists(bin_path):
                        path = bin_path
                    
                # flutter.bat'i kontrol et
                flutter_bat = os.path.join(path, "flutter.bat")
                if not os.path.exists(flutter_bat):
                    messagebox.showwarning(
                        "Uyarı",
                        "Seçilen dizinde flutter.bat bulunamadı!\n"
                        "Lütfen Flutter SDK'nın bin klasörünü seçin."
                    )
                    return
            
            self.path_var.set(path)

    def suggest_program_path(self, event=None):
        """Seçilen programa göre dizin öner"""
        program = self.program_var.get()
        
        if program == "Flutter SDK":
            # Önce FLUTTER_ROOT'u kontrol et
            flutter_root = os.environ.get('FLUTTER_ROOT', '')
            if flutter_root and os.path.exists(os.path.join(flutter_root, "bin", "flutter.bat")):
                self.path_var.set(os.path.join(flutter_root, "bin"))
                return
                
            # Git'in yüklü olup olmadığını kontrol et
            try:
                subprocess.run(['git', '--version'], check=True, capture_output=True)
            except:
                messagebox.showwarning("Uyarı", 
                    "Git yüklü değil!\nFlutter için Git gereklidir.\n"
                    "Lütfen önce Git'i yükleyin.")
        else:
            # Yaygın kurulum dizinleri
            common_paths = {
                "Node.js": [
                    "E:\\Program Files\\nodejs",
                    "C:\\Program Files\\nodejs"
                ],
                "Python": [
                    "E:\\Python310",
                    "C:\\Python310",
                    "C:\\Python311",
                    "C:\\Python312"
                ],
                "Java JDK": [
                    "E:\\Program Files\\Java\\jdk-21\\bin",
                    "C:\\Program Files\\Java\\jdk-21\\bin"
                ],
                "Android SDK": [
                    "E:\\AndroidSdk\\platform-tools",
                    os.path.expandvars("%LOCALAPPDATA%\\Android\\Sdk\\platform-tools")
                ],
                "Git": [
                    "E:\\Program Files\\Git\\cmd",
                    "C:\\Program Files\\Git\\cmd"
                ],
                "VS Code": [
                    "E:\\Program Files\\Microsoft VS Code\\bin",
                    "C:\\Program Files\\Microsoft VS Code\\bin"
                ]
            }
            
            if program in common_paths:
                for path in common_paths[program]:
                    expanded = os.path.expandvars(path)
                    if os.path.exists(expanded):
                        self.path_var.set(expanded)
                        return
            
            # Hiçbir önerilen dizin bulunamadıysa temizle
            self.path_var.set("")

    def add_to_path(self):
        """Seçili dizini PATH'e ekle"""
        path = os.path.normpath(self.path_var.get())  # Yolu normalize et
        
        if not path:
            messagebox.showwarning("Uyarı", "Lütfen bir dizin seçin!")
            return
            
        if not os.path.exists(path):
            messagebox.showwarning("Uyarı", "Seçilen dizin bulunamadı!")
            return
            
        try:
            # Mevcut PATH'i al (Kullanıcı ve Sistem PATH'lerini birleştir)
            user_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
            
            try:
                user_path = winreg.QueryValueEx(user_key, "Path")[0]
            except:
                user_path = ""
            
            # Yolları liste olarak ayır
            paths = [p.strip() for p in user_path.split(';') if p.strip()]
            
            # Yeni yolu ekle (eğer yoksa)
            if path not in paths:
                paths.append(path)
            
            # Program türüne göre ek dizinleri ekle
            program = self.program_var.get()
            if program == "Flutter SDK":
                flutter_root = os.path.dirname(os.path.dirname(path))  # bin üst dizini
                dart_sdk = os.path.join(flutter_root, "bin", "cache", "dart-sdk", "bin")
                if os.path.exists(dart_sdk) and dart_sdk not in paths:
                    paths.append(dart_sdk)
                
                # Flutter ve Dart için environment değişkenleri
                subprocess.run(['setx', 'FLUTTER_ROOT', flutter_root])
                subprocess.run(['setx', 'DART_SDK', os.path.join(flutter_root, "bin", "cache", "dart-sdk")])
            
            # Yeni PATH'i kaydet
            new_path = ';'.join(paths)
            winreg.SetValueEx(user_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(user_key)
            
            # Sistem değişkenlerini yenileme mesajı gönder
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment',
                SMTO_ABORTIFHUNG, 5000, ctypes.byref(ctypes.c_ulong())
            )
            
            messagebox.showinfo("Başarılı", 
                              f"{path}\nPATH'e eklendi!\n\n"
                              "Değişikliklerin etkili olması için:\n"
                              "1. Açık olan terminal pencerelerini kapatın\n"
                              "2. VS Code'u yeniden başlatın\n"
                              "3. Gerekirse bilgisayarı yeniden başlatın")
            
            self.scan_environments()  # Tabloyu güncelle
            
        except Exception as e:
            logging.error(f"PATH ekleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
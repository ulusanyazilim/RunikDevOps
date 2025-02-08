from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
import logging
import psutil
import re
import shutil
from mysqlfixer import find_problematic_files, delete_files, GROUP_NAMES

class XamppTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # XAMPP Dizin Seçimi
        path_frame = ttk.LabelFrame(self, text="XAMPP Dizini", padding="10")
        path_frame.pack(fill=tk.X, pady=5)
        
        self.xampp_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.xampp_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Gözat", command=self.browse_xampp).pack(side=tk.LEFT, padx=5)
        
        # Servis Durumları
        status_frame = ttk.LabelFrame(self, text="Servis Durumları", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        # Apache Durumu
        apache_frame = ttk.Frame(status_frame)
        apache_frame.pack(fill=tk.X, pady=5)
        
        self.apache_status = tk.StringVar(value="⚪ Durdu")
        ttk.Label(apache_frame, text="Apache:").pack(side=tk.LEFT, padx=5)
        ttk.Label(apache_frame, textvariable=self.apache_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(apache_frame, text="Başlat", command=self.start_apache).pack(side=tk.LEFT, padx=5)
        ttk.Button(apache_frame, text="Durdur", command=self.stop_apache).pack(side=tk.LEFT, padx=5)
        
        # MySQL Durumu
        mysql_frame = ttk.Frame(status_frame)
        mysql_frame.pack(fill=tk.X, pady=5)
        
        self.mysql_status = tk.StringVar(value="⚪ Durdu")
        ttk.Label(mysql_frame, text="MySQL:").pack(side=tk.LEFT, padx=5)
        ttk.Label(mysql_frame, textvariable=self.mysql_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(mysql_frame, text="Başlat", command=self.start_mysql).pack(side=tk.LEFT, padx=5)
        ttk.Button(mysql_frame, text="Durdur", command=self.stop_mysql).pack(side=tk.LEFT, padx=5)
        
        # Port Ayarları
        ports_frame = ttk.LabelFrame(self, text="Port Ayarları", padding="10")
        ports_frame.pack(fill=tk.X, pady=5)
        
        # Apache Portları
        apache_ports = ttk.Frame(ports_frame)
        apache_ports.pack(fill=tk.X, pady=5)
        
        ttk.Label(apache_ports, text="Apache HTTP Port:").pack(side=tk.LEFT, padx=5)
        self.apache_port = ttk.Entry(apache_ports, width=10)
        self.apache_port.pack(side=tk.LEFT, padx=5)
        self.apache_port.insert(0, "80")
        
        ttk.Label(apache_ports, text="Apache HTTPS Port:").pack(side=tk.LEFT, padx=5)
        self.apache_ssl_port = ttk.Entry(apache_ports, width=10)
        self.apache_ssl_port.pack(side=tk.LEFT, padx=5)
        self.apache_ssl_port.insert(0, "443")
        
        # MySQL Port
        mysql_ports = ttk.Frame(ports_frame)
        mysql_ports.pack(fill=tk.X, pady=5)
        
        ttk.Label(mysql_ports, text="MySQL Port:").pack(side=tk.LEFT, padx=5)
        self.mysql_port = ttk.Entry(mysql_ports, width=10)
        self.mysql_port.pack(side=tk.LEFT, padx=5)
        self.mysql_port.insert(0, "3306")
        
        ttk.Button(ports_frame, text="Portları Uygula", 
                  command=self.apply_ports).pack(pady=5)
        
        # MySQL Temizlik
        mysql_frame = ttk.LabelFrame(self, text="MySQL Temizlik", padding="10")
        mysql_frame.pack(fill=tk.X, pady=5)
        
        # Problemli dosya listesi
        self.problem_list = ttk.Treeview(mysql_frame, columns=("Grup", "Dosya", "Boyut", "Tarih"), 
                                       show="headings", height=6)
        
        self.problem_list.heading("Grup", text="Grup")
        self.problem_list.heading("Dosya", text="Dosya")
        self.problem_list.heading("Boyut", text="Boyut")
        self.problem_list.heading("Tarih", text="Tarih")
        
        self.problem_list.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(mysql_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Problemli Dosyaları Tara", 
                  command=self.scan_mysql_problems).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Dosyaları Temizle", 
                  command=self.clean_mysql_problems).pack(side=tk.LEFT, padx=5)
        
        # İlk taramayı yap
        self.detect_xampp()
        self.check_services()

    def detect_xampp(self):
        """XAMPP dizinini otomatik bul"""
        possible_paths = [
            "C:\\xampp",
            "E:\\xampp",
            "D:\\xampp",
            os.path.expandvars("%ProgramFiles%\\xampp"),
            os.path.expandvars("%ProgramFiles(x86)%\\xampp")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.xampp_path.set(path)
                return

    def browse_xampp(self):
        """XAMPP dizinini seç"""
        path = filedialog.askdirectory(title="XAMPP Dizinini Seç")
        if path:
            self.xampp_path.set(path)

    def check_services(self):
        """Apache ve MySQL durumlarını kontrol et"""
        # Apache kontrolü
        apache_running = False
        mysql_running = False
        
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] == 'httpd.exe':
                    apache_running = True
                elif proc.info['name'] == 'mysqld.exe':
                    mysql_running = True
            except:
                continue
        
        self.apache_status.set("✅ Çalışıyor" if apache_running else "⚪ Durdu")
        self.mysql_status.set("✅ Çalışıyor" if mysql_running else "⚪ Durdu")
        
        # 5 saniye sonra tekrar kontrol et
        self.after(5000, self.check_services)

    def start_apache(self):
        """Apache'yi başlat"""
        try:
            xampp_path = self.xampp_path.get()
            if not xampp_path:
                raise Exception("XAMPP dizini seçilmedi!")
                
            apache_exe = os.path.join(xampp_path, "apache\\bin\\httpd.exe")
            if not os.path.exists(apache_exe):
                raise Exception("Apache çalıştırılabilir dosyası bulunamadı!")
            
            subprocess.Popen([apache_exe])
            messagebox.showinfo("Başarılı", "Apache başlatıldı!")
            
        except Exception as e:
            logging.error(f"Apache başlatma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def stop_apache(self):
        """Apache'yi durdur"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'httpd.exe':
                    proc.kill()
            messagebox.showinfo("Başarılı", "Apache durduruldu!")
            
        except Exception as e:
            logging.error(f"Apache durdurma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def start_mysql(self):
        """MySQL'i başlat"""
        try:
            xampp_path = self.xampp_path.get()
            if not xampp_path:
                raise Exception("XAMPP dizini seçilmedi!")
                
            mysql_exe = os.path.join(xampp_path, "mysql\\bin\\mysqld.exe")
            if not os.path.exists(mysql_exe):
                raise Exception("MySQL çalıştırılabilir dosyası bulunamadı!")
            
            subprocess.Popen([mysql_exe, "--defaults-file=" + 
                            os.path.join(xampp_path, "mysql\\bin\\my.ini")])
            messagebox.showinfo("Başarılı", "MySQL başlatıldı!")
            
        except Exception as e:
            logging.error(f"MySQL başlatma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def stop_mysql(self):
        """MySQL'i durdur"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'mysqld.exe':
                    proc.kill()
            messagebox.showinfo("Başarılı", "MySQL durduruldu!")
            
        except Exception as e:
            logging.error(f"MySQL durdurma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def apply_ports(self):
        """Port ayarlarını uygula"""
        try:
            xampp_path = self.xampp_path.get()
            if not xampp_path:
                raise Exception("XAMPP dizini seçilmedi!")
            
            # Apache portlarını güncelle
            apache_conf = os.path.join(xampp_path, "apache\\conf\\httpd.conf")
            if os.path.exists(apache_conf):
                with open(apache_conf, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # HTTP port değiştir
                content = re.sub(r'Listen \d+', f'Listen {self.apache_port.get()}', content)
                content = re.sub(r'ServerName localhost:\d+', 
                               f'ServerName localhost:{self.apache_port.get()}', content)
                
                with open(apache_conf, 'w', encoding='utf-8') as f:
                    f.write(content)
                
            # SSL port güncelle
            ssl_conf = os.path.join(xampp_path, "apache\\conf\\extra\\httpd-ssl.conf")
            if os.path.exists(ssl_conf):
                with open(ssl_conf, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = re.sub(r'Listen \d+', f'Listen {self.apache_ssl_port.get()}', content)
                
                with open(ssl_conf, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # MySQL port güncelle
            mysql_ini = os.path.join(xampp_path, "mysql\\bin\\my.ini")
            if os.path.exists(mysql_ini):
                with open(mysql_ini, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = re.sub(r'port=\d+', f'port={self.mysql_port.get()}', content)
                
                with open(mysql_ini, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            messagebox.showinfo("Başarılı", 
                              "Port ayarları güncellendi!\n"
                              "Değişikliklerin etkili olması için servisleri yeniden başlatın.")
            
        except Exception as e:
            logging.error(f"Port güncelleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def scan_mysql_problems(self):
        """MySQL problemli dosyalarını tara"""
        try:
            xampp_path = self.xampp_path.get()
            if not xampp_path:
                raise Exception("XAMPP dizini seçilmedi!")
            
            mysql_data = os.path.join(xampp_path, "mysql\\data")
            if not os.path.exists(mysql_data):
                raise Exception("MySQL data dizini bulunamadı!")
            
            # Listeyi temizle
            for item in self.problem_list.get_children():
                self.problem_list.delete(item)
            
            # Problemli dosyaları bul
            _, grouped_files = find_problematic_files(mysql_data)
            
            # Dosyaları listele
            for group, files in grouped_files.items():
                group_name = GROUP_NAMES.get(group, group)
                for file in files:
                    size_mb = file['size'] / (1024 * 1024)
                    self.problem_list.insert("", tk.END, values=(
                        group_name,
                        os.path.basename(file['path']),
                        f"{size_mb:.1f} MB",
                        file['modified']
                    ))
            
        except Exception as e:
            logging.error(f"MySQL tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_mysql_problems(self):
        """Seçili problemli dosyaları temizle"""
        try:
            selected = self.problem_list.selection()
            if not selected:
                messagebox.showwarning("Uyarı", "Lütfen temizlenecek dosyaları seçin!")
                return
            
            if messagebox.askyesno("Onay", 
                "Seçili dosyalar silinecek.\nBu işlem geri alınamaz!\n"
                "Devam etmek istiyor musunuz?"):
                
                xampp_path = self.xampp_path.get()
                mysql_data = os.path.join(xampp_path, "mysql\\data")
                
                for item in selected:
                    file_name = self.problem_list.item(item)['values'][1]
                    file_path = ""
                    
                    # Dosyayı bul
                    for root, _, files in os.walk(mysql_data):
                        if file_name in files:
                            file_path = os.path.join(root, file_name)
                            break
                    
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            self.problem_list.delete(item)
                        except:
                            continue
                
                messagebox.showinfo("Başarılı", "Seçili dosyalar temizlendi!")
                
        except Exception as e:
            logging.error(f"MySQL temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
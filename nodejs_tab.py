from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import os
import logging

class NodejsTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Node.js Bilgileri
        info_frame = ttk.LabelFrame(self, text="Node.js Bilgileri", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Sürüm listesi
        columns = ("Sürüm", "Durum", "npm", "Konum")
        self.node_list = ttk.Treeview(info_frame, columns=columns, show="headings")
        
        for col in columns:
            self.node_list.heading(col, text=col)
        
        self.node_list.pack(fill=tk.X, pady=5)
        
        # NVM Yönetimi
        nvm_frame = ttk.LabelFrame(self, text="NVM (Node Version Manager)", padding="10")
        nvm_frame.pack(fill=tk.X, pady=5)
        
        # Yüklenebilir sürümler
        ttk.Label(nvm_frame, text="Yüklenebilir Sürümler:").pack(anchor=tk.W)
        self.version_combo = ttk.Combobox(nvm_frame, width=20, state="readonly")
        self.version_combo.pack(pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Sürümleri Tara", 
                  command=self.scan_versions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Sürümü Yükle", 
                  command=self.install_version).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Sürümü Varsayılan Yap", 
                  command=self.set_default).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="npm Cache Temizle", 
                  command=self.clean_npm_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kullanılmayan Sürümleri Kaldır", 
                  command=self.cleanup_versions).pack(side=tk.LEFT, padx=5)

    def scan_versions(self):
        """Node.js sürümlerini tara"""
        try:
            # Listeyi temizle
            for item in self.node_list.get_children():
                self.node_list.delete(item)
            
            # Olası Node.js dizinleri
            nodejs_paths = [
                "E:\\Program Files\\nodejs",
                "C:\\Program Files\\nodejs",
                "C:\\Program Files (x86)\\nodejs",
                os.path.expandvars("%NODE_HOME%")
            ]
            
            # PATH'ten Node.js dizinlerini bul
            path_dirs = os.environ.get('PATH', '').split(';')
            for dir in path_dirs:
                if 'node' in dir.lower():
                    base_dir = dir.rstrip('\\')
                    if os.path.exists(os.path.join(base_dir, 'node.exe')):
                        if base_dir not in nodejs_paths:
                            nodejs_paths.append(base_dir)
            
            # Bulunan dizinlerdeki Node.js'leri kontrol et
            for node_dir in nodejs_paths:
                if node_dir and os.path.exists(node_dir):
                    node_exe = os.path.join(node_dir, 'node.exe')
                    npm_cmd = os.path.join(node_dir, 'npm.cmd')
                    
                    if os.path.exists(node_exe):
                        try:
                            # Node.js sürümünü al
                            node_version = subprocess.run([node_exe, '--version'], 
                                                       capture_output=True, text=True).stdout.strip()
                            
                            # npm sürümünü al
                            npm_version = "?"
                            if os.path.exists(npm_cmd):
                                npm_version = subprocess.run([npm_cmd, '--version'], 
                                                          capture_output=True, text=True).stdout.strip()
                            
                            # PATH'te aktif mi kontrol et
                            is_active = node_dir.lower() in [p.lower() for p in path_dirs]
                            
                            self.node_list.insert("", tk.END, values=(
                                node_version,
                                "✅ Aktif" if is_active else "⚪ Pasif",
                                f"npm {npm_version}",
                                node_dir
                            ))
                        except Exception as e:
                            logging.error(f"Node.js sürüm kontrolü hatası ({node_dir}): {e}")
            
            # NVM yüklü mü kontrol et
            nvm_dir = os.path.expanduser("~\\AppData\\Roaming\\nvm")
            if os.path.exists(nvm_dir):
                for dir in os.listdir(nvm_dir):
                    if dir.startswith('v'):
                        node_path = os.path.join(nvm_dir, dir)
                        try:
                            result = subprocess.run([os.path.join(node_path, 'node.exe'), '--version'], 
                                                 capture_output=True, text=True)
                            version = result.stdout.strip()
                            
                            # npm sürümünü kontrol et
                            npm_result = subprocess.run([os.path.join(node_path, 'npm.cmd'), '--version'], 
                                                     capture_output=True, text=True)
                            npm_version = npm_result.stdout.strip()
                            
                            self.node_list.insert("", tk.END, values=(
                                version,
                                "⚪ Pasif",
                                f"npm {npm_version}",
                                node_path
                            ))
                        except:
                            continue
            
            # Yüklenebilir sürümleri güncelle
            try:
                nvm_list = subprocess.run(['nvm', 'list', 'available'], 
                                        capture_output=True, text=True)
                if nvm_list.returncode == 0:
                    versions = [v.strip() for v in nvm_list.stdout.split('\n') if v.strip()]
                    self.version_combo['values'] = versions
            except:
                pass
            
        except Exception as e:
            logging.error(f"Node.js tarama hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def install_version(self):
        """Seçili sürümü yükle"""
        version = self.version_combo.get()
        if not version:
            messagebox.showwarning("Uyarı", "Lütfen bir sürüm seçin!")
            return
            
        try:
            subprocess.run(['nvm', 'install', version], check=True)
            messagebox.showinfo("Başarılı", f"Node.js {version} yüklendi!")
            self.scan_versions()
            
        except Exception as e:
            logging.error(f"Node.js yükleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def set_default(self):
        """Seçili sürümü varsayılan yap"""
        selected = self.node_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir sürüm seçin!")
            return
            
        try:
            version = self.node_list.item(selected[0])['values'][0]
            subprocess.run(['nvm', 'use', version], check=True)
            messagebox.showinfo("Başarılı", f"Node.js {version} varsayılan yapıldı!")
            self.scan_versions()
            
        except Exception as e:
            logging.error(f"Node.js varsayılan yapma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_npm_cache(self):
        """npm önbelleğini temizle"""
        try:
            subprocess.run(['npm', 'cache', 'clean', '--force'], check=True)
            messagebox.showinfo("Başarılı", "npm önbelleği temizlendi!")
            
        except Exception as e:
            logging.error(f"npm temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def cleanup_versions(self):
        """Kullanılmayan Node.js sürümlerini kaldır"""
        if not messagebox.askyesno("Onay", 
            "Bu işlem aktif olmayan Node.js sürümlerini kaldıracak.\n"
            "Devam etmek istiyor musunuz?"):
            return
            
        try:
            for item in self.node_list.get_children():
                values = self.node_list.item(item)['values']
                if values[1] == "⚪ Pasif":
                    version = values[0]
                    subprocess.run(['nvm', 'uninstall', version], check=True)
            
            messagebox.showinfo("Başarılı", "Kullanılmayan sürümler kaldırıldı!")
            self.scan_versions()
            
        except Exception as e:
            logging.error(f"Node.js temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
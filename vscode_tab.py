from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import logging
import shutil
import json

class VSCodeTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # VS Code Eklentileri
        extensions_frame = ttk.LabelFrame(self, text="VS Code Eklentileri", padding="10")
        extensions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Eklenti listesi
        columns = ("Eklenti", "Yayıncı", "Sürüm", "Durum")
        self.ext_list = ttk.Treeview(extensions_frame, columns=columns, show="headings")
        
        for col in columns:
            self.ext_list.heading(col, text=col)
        
        self.ext_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Git Önbellek Bilgileri
        git_frame = ttk.LabelFrame(self, text="Git Önbellek Bilgileri", padding="10")
        git_frame.pack(fill=tk.X, pady=5)
        
        self.git_info = ttk.Label(git_frame, text="Git önbellek bilgileri yükleniyor...")
        self.git_info.pack(anchor=tk.W, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Eklentileri Listele", 
                  command=self.list_extensions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Eklentiyi Kaldır", 
                  command=self.remove_extension).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="VS Code Önbelleğini Temizle", 
                  command=self.clean_vscode_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Git Önbelleğini Temizle", 
                  command=self.clean_git_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Git LFS Önbelleğini Temizle", 
                  command=self.clean_git_lfs).pack(side=tk.LEFT, padx=5)
        
        # İlk taramayı yap
        self.list_extensions()
        self.update_git_info()

    def list_extensions(self):
        """VS Code eklentilerini listele"""
        try:
            # Listeyi temizle
            for item in self.ext_list.get_children():
                self.ext_list.delete(item)
            
            # VS Code yolunu bul
            vscode_paths = [
                os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd"),
                "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
                "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd"
            ]
            
            code_path = None
            for path in vscode_paths:
                if os.path.exists(path):
                    code_path = path
                    break
            
            if not code_path:
                raise Exception("VS Code bulunamadı!")
            
            # Eklentileri listele
            result = subprocess.run([code_path, '--list-extensions'], 
                                 capture_output=True, text=True)
            
            extensions = result.stdout.strip().split('\n')
            for ext in extensions:
                if ext:
                    # Her eklenti için detay al
                    try:
                        # publisher.name@version formatını parçala
                        parts = ext.split('.')
                        if len(parts) >= 2:
                            publisher = parts[0]
                            name_version = '.'.join(parts[1:]).split('@')
                            name = name_version[0]
                            version = name_version[1] if len(name_version) > 1 else "?"
                            
                            self.ext_list.insert("", tk.END, values=(
                                name,
                                publisher,
                                version,
                                "✅ Aktif"
                            ))
                    except:
                        # Hatalı format varsa en azından adını göster
                        self.ext_list.insert("", tk.END, values=(
                            ext,
                            "?",
                            "?",
                            "✅ Aktif"
                        ))
            
        except Exception as e:
            logging.error(f"Eklenti listeleme hatası: {e}")
            self.ext_list.insert("", tk.END, values=(
                "VS Code eklentileri listelenemedi!",
                "Hata",
                str(e),
                "❌"
            ))

    def remove_extension(self):
        """Seçili eklentiyi kaldır"""
        selected = self.ext_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir eklenti seçin!")
            return
            
        try:
            ext_name = self.ext_list.item(selected[0])['values'][0]
            publisher = self.ext_list.item(selected[0])['values'][1]
            
            if publisher != "?" and ext_name != "VS Code eklentileri listelenemedi!":
                # VS Code yolunu bul
                vscode_paths = [
                    os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd"),
                    "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
                    "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd"
                ]
                
                code_path = None
                for path in vscode_paths:
                    if os.path.exists(path):
                        code_path = path
                        break
                
                if not code_path:
                    raise Exception("VS Code bulunamadı!")
                
                # Eklentiyi kaldır
                full_name = f"{publisher}.{ext_name}"
                subprocess.run([code_path, '--uninstall-extension', full_name], check=True)
                messagebox.showinfo("Başarılı", f"{full_name} eklentisi kaldırıldı!")
                self.list_extensions()
            else:
                messagebox.showerror("Hata", "Bu öğe kaldırılamaz!")
            
        except Exception as e:
            logging.error(f"Eklenti kaldırma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_vscode_cache(self):
        """VS Code önbelleğini temizle"""
        try:
            cache_paths = [
                os.path.expanduser("~\\AppData\\Roaming\\Code\\Cache"),
                os.path.expanduser("~\\AppData\\Roaming\\Code\\CachedData"),
                os.path.expanduser("~\\AppData\\Roaming\\Code\\CachedExtensions"),
                os.path.expanduser("~\\AppData\\Roaming\\Code\\Code Cache")
            ]
            
            for path in cache_paths:
                if os.path.exists(path):
                    shutil.rmtree(path)
            
            messagebox.showinfo("Başarılı", "VS Code önbelleği temizlendi!")
            
        except Exception as e:
            logging.error(f"VS Code önbellek temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def update_git_info(self):
        """Git önbellek bilgilerini güncelle"""
        try:
            # Git önbellek boyutunu hesapla
            git_cache = os.path.expanduser("~\\.git")
            git_lfs = os.path.expanduser("~\\.git-lfs")
            
            git_size = self.get_folder_size(git_cache) if os.path.exists(git_cache) else 0
            lfs_size = self.get_folder_size(git_lfs) if os.path.exists(git_lfs) else 0
            
            info_text = f"Git Önbellek: {git_size/1024/1024:.1f} MB\n"
            info_text += f"Git LFS Önbellek: {lfs_size/1024/1024:.1f} MB"
            
            self.git_info.config(text=info_text)
            
        except Exception as e:
            logging.error(f"Git bilgi güncelleme hatası: {e}")
            self.git_info.config(text="Git bilgileri alınamadı!")

    def clean_git_cache(self):
        """Git önbelleğini temizle"""
        try:
            # Git'in yüklü olduğunu kontrol et
            result = subprocess.run(['where', 'git'], capture_output=True, text=True)
            if 'git.exe' not in result.stdout:
                raise Exception("Git yüklü değil!")
                
            # Geçerli dizinde git repo olup olmadığını kontrol et
            home = os.path.expanduser("~")
            os.chdir(home)  # Kullanıcı dizinine geç
            
            subprocess.run(['git', 'gc', '--aggressive', '--prune=now'], check=True)
            subprocess.run(['git', 'clean', '-fdx'], check=True)
            messagebox.showinfo("Başarılı", "Git önbelleği temizlendi!")
            self.update_git_info()
            
        except Exception as e:
            logging.error(f"Git temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def clean_git_lfs(self):
        """Git LFS önbelleğini temizle"""
        try:
            subprocess.run(['git', 'lfs', 'prune'], check=True)
            messagebox.showinfo("Başarılı", "Git LFS önbelleği temizlendi!")
            self.update_git_info()
            
        except Exception as e:
            logging.error(f"Git LFS temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def get_folder_size(self, path):
        """Klasör boyutunu hesapla"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size 
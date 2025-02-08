from base_tab import BaseTab
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import logging
from threading import Thread

class DockerTab(BaseTab):
    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Docker Konteynerler
        containers_frame = ttk.LabelFrame(self, text="Docker Konteynerler", padding="10")
        containers_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Konteyner listesi
        columns = ("ID", "İsim", "Image", "Durum", "Port", "Boyut")
        self.container_list = ttk.Treeview(containers_frame, columns=columns, show="headings")
        
        for col in columns:
            self.container_list.heading(col, text=col)
        
        self.container_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Images Frame
        images_frame = ttk.LabelFrame(self, text="Docker Images", padding="10")
        images_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Image listesi
        img_columns = ("ID", "Repository", "Tag", "Boyut", "Oluşturma")
        self.image_list = ttk.Treeview(images_frame, columns=img_columns, show="headings")
        
        for col in img_columns:
            self.image_list.heading(col, text=col)
        
        self.image_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Yenile", 
                  command=self.refresh_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Konteyneri Başlat", 
                  command=self.start_container).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Konteyneri Durdur", 
                  command=self.stop_container).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seçili Image'ı Sil", 
                  command=self.remove_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kullanılmayan Nesneleri Temizle", 
                  command=self.docker_prune).pack(side=tk.LEFT, padx=5)

    def refresh_all(self):
        """Tüm listeleri yenile"""
        Thread(target=self.refresh_containers).start()
        Thread(target=self.refresh_images).start()

    def refresh_containers(self):
        """Konteyner listesini yenile"""
        try:
            # Listeyi temizle
            for item in self.container_list.get_children():
                self.container_list.delete(item)
            
            # Docker konteynerlerini al
            result = subprocess.run(['docker', 'ps', '-a', '--format', '{{json .}}'], 
                                 capture_output=True, text=True)
            
            containers = result.stdout.strip().split('\n')
            for container in containers:
                if container:
                    data = json.loads(container)
                    self.container_list.insert("", tk.END, values=(
                        data.get('ID', '')[:12],
                        data.get('Names', ''),
                        data.get('Image', ''),
                        data.get('Status', ''),
                        data.get('Ports', ''),
                        data.get('Size', '')
                    ))
                    
        except Exception as e:
            logging.error(f"Konteyner yenileme hatası: {e}")

    def refresh_images(self):
        """Image listesini yenile"""
        try:
            # Listeyi temizle
            for item in self.image_list.get_children():
                self.image_list.delete(item)
            
            # Docker image'larını al
            result = subprocess.run(['docker', 'images', '--format', '{{json .}}'], 
                                 capture_output=True, text=True)
            
            images = result.stdout.strip().split('\n')
            for image in images:
                if image:
                    data = json.loads(image)
                    self.image_list.insert("", tk.END, values=(
                        data.get('ID', '')[:12],
                        data.get('Repository', ''),
                        data.get('Tag', ''),
                        data.get('Size', ''),
                        data.get('CreatedAt', '')
                    ))
                    
        except Exception as e:
            logging.error(f"Image yenileme hatası: {e}")

    def start_container(self):
        """Seçili konteyneri başlat"""
        selected = self.container_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir konteyner seçin!")
            return
            
        try:
            container_id = self.container_list.item(selected[0])['values'][0]
            subprocess.run(['docker', 'start', container_id], check=True)
            self.refresh_containers()
            
        except Exception as e:
            logging.error(f"Konteyner başlatma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def stop_container(self):
        """Seçili konteyneri durdur"""
        selected = self.container_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir konteyner seçin!")
            return
            
        try:
            container_id = self.container_list.item(selected[0])['values'][0]
            subprocess.run(['docker', 'stop', container_id], check=True)
            self.refresh_containers()
            
        except Exception as e:
            logging.error(f"Konteyner durdurma hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def remove_image(self):
        """Seçili image'ı sil"""
        selected = self.image_list.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir image seçin!")
            return
            
        try:
            image_id = self.image_list.item(selected[0])['values'][0]
            subprocess.run(['docker', 'rmi', image_id], check=True)
            self.refresh_images()
            
        except Exception as e:
            logging.error(f"Image silme hatası: {e}")
            messagebox.showerror("Hata", str(e))

    def docker_prune(self):
        """Kullanılmayan Docker nesnelerini temizle"""
        if not messagebox.askyesno("Onay", 
            "Bu işlem kullanılmayan tüm Docker nesnelerini temizleyecek.\n"
            "Devam etmek istiyor musunuz?"):
            return
            
        try:
            # Kullanılmayan konteynerler
            subprocess.run(['docker', 'container', 'prune', '-f'], check=True)
            # Kullanılmayan imageler
            subprocess.run(['docker', 'image', 'prune', '-f'], check=True)
            # Kullanılmayan volumeler
            subprocess.run(['docker', 'volume', 'prune', '-f'], check=True)
            # Kullanılmayan networkler
            subprocess.run(['docker', 'network', 'prune', '-f'], check=True)
            
            messagebox.showinfo("Başarılı", "Docker temizliği tamamlandı!")
            self.refresh_all()
            
        except Exception as e:
            logging.error(f"Docker temizleme hatası: {e}")
            messagebox.showerror("Hata", str(e)) 
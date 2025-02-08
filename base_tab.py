import tkinter as tk
from tkinter import ttk, messagebox
import logging

class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Alt sınıflar bu metodu override etmeli"""
        pass
        
    def update_status(self, message, progress=None):
        """Durum mesajını ve ilerleme çubuğunu güncelle"""
        try:
            if hasattr(self, 'status_var'):
                self.status_var.set(message)
            if progress is not None and hasattr(self, 'progress'):
                self.progress['value'] = progress
            self.update()
            logging.info(message)
        except Exception as e:
            logging.error(f"Durum güncellemesi hatası: {e}") 
from constants import *
import tkinter as tk
import customtkinter as ctk
import time

class Length(Stage):
    def setup(self, frame):
        super().setup(frame)
        self.length_var = tk.StringVar()
        self.length_widget = ctk.CTkLabel(self.frame, textvariable=self.length_var)

    @staticmethod
    def update(text):
        length = len(text)

        return (length,)

    def update_widgets(self, length):
        self.length_var.set(length)
    
    def display(self):
        self.length_widget.grid(row=0, column=0)

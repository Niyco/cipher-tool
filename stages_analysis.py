from constants import *
import tkinter as tk
import customtkinter as ctk

class Length(Stage):
    def setup(self, frame):
        super().setup(frame)
        self.length_var = tk.StringVar()
        self.length_var.set('0')
        self.length_widget = ctk.CTkLabel(self.frame, textvariable=self.length_var)

    @staticmethod
    def update(text):
        length = len(text)

        return (length,)

    def update_widgets(self, length):
        self.length_var.set(length)
    
    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.length_widget.grid(row=0, column=0)

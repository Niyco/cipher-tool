import tkinter as tk
import customtkinter as ctk

class Length:
    def __init__(self, frame, update_ouput):
        self.frame = frame
    
    def setup(self, frame):
        self.length = tk.StringVar()
        self.length_widget = ctk.CTkLabel(self.frame, textvariable=self.length)
        
    def update(self, text):
        return self.length.set(len(text))
    
    def display(self):
        self.length_widget.grid(row=0, column=0)

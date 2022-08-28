import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

root = ctk.CTk()
icon = tk.PhotoImage(file=r'resources\icon.png')

ctk.set_appearance_mode('light')
root.title('Cipher Tool')
root.geometry('1366x768')
root.iconphoto(False, icon)

root.mainloop()

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
icon = tk.PhotoImage(file=r'resources\icon.png')
root.title('Cipher Tool')
root.geometry('1366x768')
root.iconphoto(False, icon)

root.mainloop()

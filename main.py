from constants import *
import customtkinter as ctk
import tkinter as tk
import json

def toolbar_animation(start, stop, step, delay):
    global toolbar_animated
    toolbar.config(height=start, width=root.winfo_width())
    if start != stop:
        toolbar.after(delay, toolbar_animation, start + step, stop, step, delay)
    else:
        toolbar_animated = False

def toggle_toolbar():
    global toolbar_animated
    if not toolbar_animated:
        global toolbar_active
        
        toolbar_active = not toolbar_active
        if toolbar_active:
            toolbar_animated = True
            toolbar_animation(0, toolbar_size, 1, int(toolbar_animation_time / toolbar_size))
        else:
            toolbar_animated = True
            toolbar_animation(toolbar_size, 0, -1, int(toolbar_animation_time / toolbar_size))

def resize(event):
    if isinstance(event.widget, ctk.windows.ctk_tk.CTk) and not toolbar_animated:
        if toolbar_active:
            toolbar.config(height=toolbar_size, width=event.width)
        else:
            toolbar.config(height=0, width=event.width)

lang_file = open(lang_path)
lang = json.load(lang_file)
lang_file.close

root = ctk.CTk()
root.bind("<Configure>", resize)
icon = tk.PhotoImage(file=icon_path)
toolbar_toggle_image = tk.PhotoImage(file=toolbar_icon_path)

ctk.set_appearance_mode(mode)
root.title(lang['title'])
root.geometry(default_size)
root.minsize(int(min_size.split('x')[0]), int(min_size.split('x')[1]))
root.iconphoto(False, icon)

toolbar = ctk.CTkFrame(root)
toolbar.grid_propagate(0)
toolbar.config(height=0)
toolbar.grid(row=0, column=0, columnspan=3)
toolbar_active = False
toolbar_animated = False

hover_color = '#' + ''.join([format(min(max(int(root['bg'].lstrip('#')[i - 1:i + 1], 16) + hover_color_change, 0), 255), '02X') for i in range(1, 7, 2)])
toolbar_toggle = ctk.CTkButton(root, text='', image=toolbar_toggle_image, command=toggle_toolbar, width=42, height=30, fg_color=root['bg'], hover_color=hover_color)
toolbar_toggle.grid(row=1, column=0, padx=5, pady=5, sticky='W')

ctk.CTkLabel(toolbar, text='Toolbar').grid(row=0, column=0)

ctk.CTkLabel(root, text=lang['stage_content']).grid(row=1, column=0)
ctk.CTkLabel(root, text=lang['stage_list']).grid(row=1, column=1)
ctk.CTkLabel(root, text=lang['output']).grid(row=1, column=2)
ctk.CTkTextbox(root).grid(row=2, column=0, sticky='NESW')
ctk.CTkTextbox(root).grid(row=2, column=2, sticky='NESW')
root.columnconfigure(0, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)

root.mainloop()

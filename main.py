from constants import *
import customtkinter as ctk
import tkinter as tk
import json

def toolbar_animation(start, stop, step, delay):
    global toolbar_active
    global toolbar_animated
    
    toolbar.config(height=start, width=root.winfo_width())
    if start * (step / abs(step)) < stop:
        toolbar.after(delay, toolbar_animation, start + step, stop, step, delay)
    else:
        if not toolbar_active:
            toolbar.place(x=0,y=-1)
        toolbar_animated = False

def toggle_toolbar():
    global toolbar_active
    global toolbar_animated
    
    if not toolbar_animated:
        toolbar_active = not toolbar_active
        if toolbar_active:
            toolbar.grid(row=0, column=0, columnspan=3)
            toolbar_animated = True
            toolbar_animation(0, toolbar_size, toolbar_step,
                              int(toolbar_animation_time / toolbar_size * toolbar_step))
        else:
            toolbar_animated = True
            toolbar_animation(toolbar_size, 0, -toolbar_step,
                              int(toolbar_animation_time / toolbar_size * toolbar_step))

def resize(event):
    if isinstance(event.widget, ctk.windows.ctk_tk.CTk) and not toolbar_animated:
        if toolbar_active:
            toolbar.config(height=toolbar_size, width=event.width)
        else:
            toolbar.config(height=0, width=event.width)

def adjust(color, amount):
    new_hex = ''
    for i in range(2, 8, 2):
        adjusted = int(color[i - 1:i + 1], 16) + amount
        new_hex += format(min(max(adjusted, 0), 255), '02X')
    return '#' + new_hex

def radio_select(button):
    global radio_selected

    radio_buttons[radio_selected].configure(fg_color=theme['color']['button'][mode_int],
                                            hover_color=theme['color']['button_hover'][mode_int])
    radio_buttons[button].configure(fg_color=radio_selected_color, hover_color=radio_selected_color)
    radio_selected = button

lang_file = open(lang_path)
lang = json.load(lang_file)
lang_file.close()
theme_file = open(theme_path)
theme = json.load(theme_file)
theme_file.close()

root = ctk.CTk()
icon = tk.PhotoImage(file=icon_path)
toolbar_toggle_image = tk.PhotoImage(file=toolbar_icon_path)
if mode == 'light': mode_int = 0
else: mode_int = 1

root.title(lang['title'])
root.iconphoto(False, icon)
root.geometry(default_size)
root.bind('<Configure>', resize)
root.minsize(int(min_size.split('x')[0]), int(min_size.split('x')[1]))
ctk.set_appearance_mode(mode)
ctk.set_default_color_theme(theme_path)

toolbar = ctk.CTkFrame(root)
toolbar.grid_propagate(0)
toolbar_active = False
toolbar_animated = False
radio_text = ctk.CTkButton(toolbar, text=lang['radio_text'], height=26,
                           corner_radius=10, command=lambda: radio_select(0))
radio_analysis = ctk.CTkButton(toolbar, text=lang['radio_analysis'], height=26,
                               corner_radius=10, command=lambda: radio_select(1))
radio_cipher = ctk.CTkButton(toolbar, text=lang['radio_cipher'], height=26,
                             corner_radius=10, command=lambda: radio_select(2))
radio_text.place(x=-10, y=0)
radio_analysis.place(x=-10, y=25)
radio_cipher.place(x=-10, y=50)
radio_buttons = [radio_text, radio_analysis, radio_cipher]
radio_selected = 0
radio_select(0)

ctk.CTkButton(root, text='', image=toolbar_toggle_image,
              width=42, height=30, fg_color=root['bg'],
              hover_color=adjust(root['bg'], hover_color_change), command=toggle_toolbar
              ).grid(row=1, column=0, padx=5, pady=5, sticky='W')
ctk.CTkLabel(root, text=lang['stage_content']).grid(row=1, column=0)
ctk.CTkLabel(root, text=lang['stage_list']).grid(row=1, column=1)
ctk.CTkLabel(root, text=lang['output']).grid(row=1, column=2)
ctk.CTkTextbox(root).grid(row=2, column=0, sticky='NESW')
ctk.CTkTextbox(root).grid(row=2, column=2, sticky='NESW')

root.columnconfigure(0, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)

root.mainloop()

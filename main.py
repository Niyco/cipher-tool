from constants import *
import customtkinter as ctk
import tkinter as tk
import json

def toolbar_animation(toolbar_active, start, stop, step, delay):
    global toolbar_animated

    toolbar.config(height=start, width=root.winfo_width())
    if start * (step / abs(step)) < stop:
        toolbar.after(delay, toolbar_animation, toolbar_active, start + step, stop, step, delay)
    else:
        if not toolbar_active:
            toolbar.place(x=0, y=-1)
        toolbar_animated = False

def toggle_toolbar():
    global toolbar_active, toolbar_animated
    
    if not toolbar_animated:
        toolbar_active = not toolbar_active
        if toolbar_active:
            toolbar.grid(row=0, column=0, columnspan=3)
            toolbar_animated = True
            toolbar_animation(toolbar_active, 0, toolbar_size, toolbar_step,
                              int(toolbar_animation_time / toolbar_size * toolbar_step))
        else:
            toolbar_animated = True
            toolbar_animation(toolbar_active, toolbar_size, 0, -toolbar_step,
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

    radio_buttons[radio_selected].configure(fg_color=color_radio_deselected[mode],
                                            hover_color=color_radio_deselected[mode])
    radio_buttons[button].configure(fg_color=theme['color']['button'][mode],
                                    hover_color=theme['color']['button'][mode])
    radio_selected = button

def create_widgets():
    global toolbar, toolbar_active, tooblar_animated, radio_buttons, radio_selected, stages_canvas

    toolbar_active = False
    toolbar_animated = False
    radio_selected = 0
    
    toolbar = ctk.CTkFrame(root)
    toolbar.grid_propagate(0)
    radio_text = ctk.CTkButton(toolbar, text=lang['radio_text'], height=26,
                               corner_radius=10, command=lambda: radio_select(0),
                               fg_color=color_radio_deselected[mode], hover=False)
    radio_analysis = ctk.CTkButton(toolbar, text=lang['radio_analysis'], height=26,
                                   corner_radius=10, command=lambda: radio_select(1),
                                   fg_color=color_radio_deselected[mode], hover=False)
    radio_cipher = ctk.CTkButton(toolbar, text=lang['radio_cipher'], height=26,
                                 corner_radius=10, command=lambda: radio_select(2),
                                 fg_color=color_radio_deselected[mode], hover=False)
    radio_text.place(x=-10, y=0)
    radio_analysis.place(x=-10, y=25)
    radio_cipher.place(x=-10, y=50)
    radio_buttons = [radio_text, radio_analysis, radio_cipher]
    stages_canvas = ctk.CTkCanvas(root, bg=['#EBEBEC', '#212325'][mode], highlightthickness=0)
    stages_canvas.columnconfigure(0, weight=1)
    stages_canvas.grid(row=2, column=1, sticky='NESW')

    ctk.CTkButton(root, text='', image=toolbar_toggle_image,
                  width=42, height=30, fg_color=root['bg'],
                  hover_color=adjust(root['bg'], hover_color_change), command=toggle_toolbar
                  ).grid(row=1, column=0, padx=5, pady=5, sticky='W')
    ctk.CTkLabel(root, text=lang['stage_content']).grid(row=1, column=0)
    ctk.CTkLabel(root, text=lang['stage_list']).grid(row=1, column=1)
    ctk.CTkLabel(root, text=lang['output']).grid(row=1, column=2)
    ctk.CTkTextbox(root).grid(row=2, column=0, sticky='NESW')
    ctk.CTkTextbox(root).grid(row=2, column=2, sticky='NESW')

def update_window():
    global lang, theme, mode, stage_up_image, stage_down_image
    
    lang_file = open(lang_path + '\\' + lang_name + '.json')
    lang = json.load(lang_file)
    lang_file.close()
    theme_file = open(theme_path + '\\' + theme_name + '.json')
    theme = json.load(theme_file)
    theme_file.close()
    
    if mode_name == 'light': mode = 0
    else: mode = 1
    stage_up_image = tk.PhotoImage(file=path_stage_up[mode])
    stage_down_image = tk.PhotoImage(file=path_stage_down[theme_name][mode])
    root.title(lang['title'])

    ctk.set_appearance_mode(mode_name)
    ctk.set_default_color_theme(theme_path + '\\' + theme_name + '.json')

    for widget in root.winfo_children():
        widget.destroy()
    create_widgets()
    
root = ctk.CTk()
icon = tk.PhotoImage(file=path_window_icon)
toolbar_toggle_image = tk.PhotoImage(file=path_toolbar_icon)
toolbar_animated = False

root.iconphoto(False, icon)
root.geometry(default_size)
root.bind('<Configure>', resize)
root.minsize(int(min_size.split('x')[0]), int(min_size.split('x')[1]))
root.columnconfigure(0, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)

update_window()
radio_select(0)

root.mainloop()

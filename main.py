import customtkinter as ctk
import tkinter as tk

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

window_width, window_height = 0, 0

root = ctk.CTk()
root.bind("<Configure>", resize)
icon = tk.PhotoImage(file=r'resources\icon.png')
toolbar_toggle_image = tk.PhotoImage(file=r'resources\toolbar.png')
hover_color_change = -20
toolbar_size = 50
toolbar_animation_time = 100

ctk.set_appearance_mode('dark')
root.title('Cipher Tool')
root.geometry('1366x768')
root.iconphoto(False, icon)

toolbar = ctk.CTkFrame(root)
toolbar.grid_propagate(0)
toolbar.config(height=0)
toolbar.grid(row=0, column=0, columnspan=3)
toolbar_active = False
toolbar_animated = False

hover_color = '#' + ''.join([format(min(max(int(root['bg'].lstrip('#')[i - 1:i + 1], 16) + hover_color_change, 0), 255), '02X') for i in range(1, 7, 2)]) # Lighten/darken background color by hover_color_change
toolbar_toggle = ctk.CTkButton(root, text='', image=toolbar_toggle_image, command=toggle_toolbar, width=42, height=30, fg_color=root['bg'], hover_color=hover_color) # Note colors are not updated when theme is
toolbar_toggle.grid(row=1, column=0, padx=5, pady=5, sticky='W')

root.mainloop()

if __name__ == '__main__':
    from constants import *
    from stages_text import *
    import tkinter as tk
    import customtkinter as ctk
    import darkdetect
    import multiprocessing
    import json

    class Input:
        def __init__(self, frame, update_ouput):
            self.update_output = update_ouput
            self.input = ''
            self.setup(frame)

        def setup(self, frame):
            self.input_widget = tk.Text(frame, bd=0, bg=theme['color']['entry'][mode],
                                        font=(theme['text']['Windows']['font'],
                                               theme['text']['Windows']['size']),
                                         fg=theme['color']['text'][mode],
                                        insertbackground=theme['color']['text'][mode])
            self.input_widget.insert(1.0, self.input)
            self.input_widget.bind('<<Modified>>', self.on_modify)

        def on_modify(self, event):
            self.input_widget.tk.call(self.input_widget._w, 'edit', 'modified', 0)
            self.input = self.input_widget.get(1.0, 'end')
            self.update_output(self)

        def display(self):
            self.input_widget.grid(padx=8, pady=8, sticky='NESW')
        
    def resize(event):
        if isinstance(event.widget, ctk.windows.ctk_tk.CTk) and not toolbar_animated:
            if toolbar_active:
                toolbar.config(height=toolbar_size, width=event.width)
            else:
                toolbar.config(height=0, width=event.width)
        elif isinstance(event.widget, tk.Canvas) and str(event.widget).startswith('.!canvas'):
            for stage in current_stages:
                text_y = stages_canvas.coords(stage[2])[1]
                image_y = stages_canvas.coords(stage[1])[1]
                stages_canvas.coords(stage[2], event.width // 2, text_y)
                stages_canvas.coords(stage[1], event.width // 2, image_y)

    def create_widgets():
        global toolbar, toolbar_active, tooblar_animated, radio_buttons
        global stages_canvas, current_stages, stage_frame, stage_output

        toolbar_animated = False
        bg_color = named_to_hex(theme['color']['bg_color'][mode])
        
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
        stages_canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0, width=200)
        stages_canvas.columnconfigure(0, weight=1)
        stages_canvas.grid(row=2, column=1, sticky='NESW')
        stages_canvas.bind('<Configure>', resize)
        stage_frame = ctk.CTkFrame(root, fg_color=named_to_hex(theme['color']['entry'][mode]))
        stage_frame.grid(row=2, column=0, sticky='NESW')
        stage_frame.columnconfigure(0, weight=1)
        stage_frame.rowconfigure(0, weight=1)
        stage_frame.grid_propagate(0)
        output_frame = ctk.CTkFrame(root, fg_color=named_to_hex(theme['color']['entry'][mode]))
        output_frame.grid(row=2, column=2, sticky='NESW')
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.grid_propagate(0)
        stage_output = tk.Text(output_frame, bd=0, state='disabled', bg=theme['color']['entry'][mode],
                                        font=(theme['text']['Windows']['font'],
                                               theme['text']['Windows']['size']),
                                         fg=theme['color']['text'][mode],
                                        insertbackground=theme['color']['text'][mode])
        stage_output.grid(padx=8, pady=8, sticky='NESW')

        ctk.CTkButton(root, text='', image=toolbar_toggle_image,
                      width=42, height=30, fg_color=bg_color,
                      hover_color=adjust(bg_color, hover_color_change), command=toggle_toolbar
                      ).grid(row=1, column=0, padx=5, pady=5, sticky='W')
        ctk.CTkLabel(root, text=lang['stage_content']).grid(row=1, column=0)
        ctk.CTkLabel(root, text=lang['stage_list']).grid(row=1, column=1)
        ctk.CTkLabel(root, text=lang['output']).grid(row=1, column=2)

        to_add = current_stages.copy()
        current_stages = []
        for stage in to_add:
            add_stage(0, type(stage[0]).__name__, stage[0])

    def update_window():
        global lang, theme, mode, stage_up_image, stage_down_image, toolbar_active, selected_stage
        
        lang_file = open(lang_path + '\\' + lang_name + '.json')
        lang = json.load(lang_file)
        lang_file.close()
        theme_file = open(theme_path + '\\' + theme_name + '.json')
        theme = json.load(theme_file)
        theme_file.close()
        
        if mode_name == 'light': mode = 0
        elif mode_name == 'dark': mode = 1
        else: mode = modes.index(darkdetect.theme().lower())
            
        stage_up_image = tk.PhotoImage(file=path_stage_up[mode])
        stage_down_image = tk.PhotoImage(file=path_stage_down[theme_name][mode])
        root.title(lang['title'])

        ctk.set_appearance_mode(mode_name)
        ctk.set_default_color_theme(theme_path + '\\' + theme_name + '.json')    
        for widget in root.winfo_children():
            widget.destroy()
        create_widgets()

        if toolbar_active:
            toolbar_active = False
            toggle_toolbar()
        radio_select(radio_selected)
        if selected_stage >= 0:
            index = selected_stage
            selected_stage = -1
            switch_stage(index)

    def check_queue():
        try:
            queue.get(False)
            update_window()
        except:
            pass
        root.after(check_queue_delay, check_queue)

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
    
    def adjust(color, amount):
        new_hex = '#'
        for i in range(2, 8, 2):
            adjusted = int(color[i - 1:i + 1], 16) + amount
            new_hex += format(min(max(adjusted, 0), 255), '02X')
            
        return new_hex

    def named_to_hex(color):
        if color.startswith('#'):
            return color
        color_hex = '#'
        for value in root.winfo_rgb(color):
            color_hex += format(value // 256, '02X')
        
        return color_hex

    def set_output(text):
        stage_output.configure(state='normal')
        stage_output.delete(1.0, 'end')
        stage_output.insert(1.0, text)
        stage_output.configure(state='disabled')

    def radio_select(button):
        global radio_selected

        radio_buttons[radio_selected].configure(fg_color=color_radio_deselected[mode],
                                                hover_color=color_radio_deselected[mode])
        radio_buttons[button].configure(fg_color=named_to_hex(theme['color']['button'][mode]),
                                        hover_color=named_to_hex(theme['color']['button'][mode]))
        radio_selected = button

    def create_stage(stage, stage_type):
        name = stage.__name__
        defined_stages[stage_type][name] = stage
    
    def add_stage(stage_type, name, stage=None):
        length = len(current_stages)
        display_name = lang['stage_' + name.lower()]

        y = (stage_up_image.height() + stage_spaceing) * (length + 1)
        image = stages_canvas.create_image(0, y, image=stage_up_image)
        text = stages_canvas.create_text(0, y - 4, text=display_name,
                                         font=(theme['text']['Windows']['font'],
                                               theme['text']['Windows']['size'] + 2),
                                         fill=theme['color']['text'][mode])
        stages_canvas.tag_bind(image, "<Button-1>", lambda event: switch_stage(length))
        stages_canvas.tag_bind(text, "<Button-1>", lambda event: switch_stage(length))

        if stage:
            stage.setup(stage_frame)
        else:
            stage = defined_stages[stage_type][name](stage_frame, update_output)
        current_stages.append((stage, image, text))

        if name == 'Input':
            results.append(stage.input)
        else:
            results.append(stage.update(results[-1]))
            
        set_output(results[-1])

    def switch_stage(index):
        global selected_stage
        
        if selected_stage != index:
            stages_canvas.itemconfigure(current_stages[index][1], image=stage_down_image)
            stages_canvas.move(current_stages[index][2], 0, 4)
            if selected_stage >= 0:
                stages_canvas.itemconfigure(current_stages[selected_stage][1], image=stage_up_image)
                stages_canvas.move(current_stages[selected_stage][2], 0, -4)
            selected_stage = index

            for widget in stage_frame.winfo_children():
                widget.grid_forget()
            stage = current_stages[selected_stage][0]
            stage.display()

    def update_output(stage):
        stage_index = [i for i, v in enumerate(current_stages) if v[0] is stage][0]
        updating_stages = []
        for i in range(stage_index, len(current_stages)):
            x = current_stages[i]
            for y in defined_stages[0]:
                if isinstance(x[0], defined_stages[0][y]):
                    updating_stages.append(x[0])
                    
            for y in defined_stages[2]:
                if isinstance(x[0], defined_stages[0][y]):
                    updating_stages.append(x[0])
        
        if stage_index == 0:
            results[0] = current_stages[0][0].input
        for i in range(0, len(updating_stages)):
            results[i + 1] = updating_stages[i].update(results[i])

        set_output(results[-1])

    root = ctk.CTk()
    icon = tk.PhotoImage(file=path_window_icon)
    toolbar_toggle_image = tk.PhotoImage(file=path_toolbar_icon)
    queue = multiprocessing.Queue()
    x = multiprocessing.Process(target=darkdetect.listener, args=(queue.put,))
    x.daemon = True
    x.start()
    toolbar_active = False
    toolbar_animated = False
    modes = ['light', 'dark']
    radio_selected = 0
    selected_stage = -1
    defined_stages = [{}, {}, {}]
    current_stages = []
    results = []

    root.iconphoto(False, icon)
    root.geometry(default_size)
    root.bind('<Configure>', resize)
    root.minsize(int(min_size.split('x')[0]), int(min_size.split('x')[1]))
    root.columnconfigure(0, weight=1)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(2, weight=1)
    
    check_queue()
    update_window()

    create_stage(UpperCase, 0)

    add_stage(0, 'Input', Input(stage_frame, update_output))
    add_stage(0, 'UpperCase')
    switch_stage(0)

    root.mainloop()

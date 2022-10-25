def output_thread(queue_in, queue_out):
    while True:
        updates = queue_in.get()
        text = updates.pop(0)
        returns = []
        for update in updates:
            function, args, analysis = update
            result = function(text, *args)
            returns.append(result)
            if not analysis: text = result[0]
        queue_out.put(returns)

if __name__ == '__main__':
    from stages_text import *
    from stages_analysis import *
    import constants
    import tkinter as tk
    import customtkinter as ctk
    import sys
    import multiprocessing
    import darkdetect
    import importlib
    import json
    import time

    class Input(constants.Stage):
        def __init__(self, update_output):
            super().__init__(update_output)
            self.input = ''

        def setup(self, frame, texts):
            super().setup(frame, texts)
            self.input_widget = tk.Text(frame, bd=0, bg=constants.theme['color']['entry'][constants.mode],
                                        font=(constants.theme['text'][constants.os]['font'], font_size),
                                         fg=constants.theme['color']['text'][constants.mode],
                                        insertbackground=constants.theme['color']['text'][constants.mode])
            self.input_widget.insert(1.0, self.input)
            self.input_widget.bind('<<Modified>>', self.on_modify)
            self.input_widget.bind('<Control-BackSpace>', self.ctrl_backspace)
            self.modified = False

        def on_modify(self, event):
            self.modified = not self.modified
            if self.modified:
                self.input_widget.edit_modified(False)
                self.input = self.input_widget.get(1.0, 'end').removesuffix('\n')
                self.update_output(self)

        def ctrl_backspace(self, event):
            text = self.input_widget.get('1.0', 'insert')
            end = max(text.rfind(' '), text.rfind('\n'))
            self.input_widget.delete(1.0, 'end')
            self.input_widget.insert(1.0, self.input[:end + 1].rstrip())

            return 'break'

        def display(self):
            self.frame.columnconfigure(0, weight=1)
            self.frame.rowconfigure(0, weight=1)
            self.input_widget.grid(padx=8, pady=8, sticky='NESW')
        
    def resize(event):
        if isinstance(event.widget, ctk.windows.ctk_tk.CTk) and not toolbar_animated:
            if toolbar_active:
                toolbar.config(height=72, width=event.width)
            else:
                toolbar.config(height=0, width=event.width)

        elif event.widget == toolbar_canvas:
            toolbar_scroll(None)
        elif event.widget is stages_canvas:
            stage_scroll(None)
    
    def create_widgets():
        global toolbar, tooblar_animated, radio_buttons, stages_canvas, stage_frame, stage_output
        global results, current_stages, stage_positions, selected_stage, toolbar_canvas, max_result
        global toolbar_stages_pos, stages_pos, dragged_stage, loading_animation_label, loading

        toolbar_animated = False
        toolbar_stages_pos = 0
        stages_pos = 0
        dragged_stage = -1
        loading = False
        bg_color = named_to_hex(constants.theme['color']['bg_color'][constants.mode])

        toolbar = ctk.CTkFrame(root, fg_color=bg_color)
        toolbar.grid_propagate(0)
        toolbar.columnconfigure(1, weight=1)
        toolbar_radio = ctk.CTkFrame(toolbar, fg_color=bg_color, width=180)
        toolbar_radio.grid(row=0, column=0, sticky='NE')
        toolbar_menu = ctk.CTkFrame(toolbar, fg_color=bg_color, width=230)
        toolbar_menu.grid(row=0, column=2, sticky='NW')
        toolbar_canvas = tk.Canvas(toolbar, bg=bg_color, highlightthickness=0)
        toolbar_canvas.grid(row=0, column=1, sticky='EW')
        toolbar_canvas.bind('<MouseWheel>', toolbar_scroll)

        toolbar_canvas.create_rectangle(0, 0, 0, 0, outline=constants.theme['color']['deselected'][constants.mode])
        ctk.CTkLabel(toolbar_radio, image=toolbar_separator_image).place(x=85, y=0)
        ctk.CTkLabel(toolbar_menu, image=toolbar_separator_image).place(x=-45, y=0)
        radio_text_button = ctk.CTkButton(toolbar_radio, text=constants.lang['radio_text'], height=24,
                                          corner_radius=10, command=lambda: radio_select(0),
                                          fg_color=constants.theme['color']['deselected'][constants.mode],
                                          hover=False)
        radio_analysis_button = ctk.CTkButton(toolbar_radio, text=constants.lang['radio_analysis'], height=24,
                                              corner_radius=10, command=lambda: radio_select(1),
                                              fg_color=constants.theme['color']['deselected'][constants.mode],
                                              hover=False)
        radio_cipher_button = ctk.CTkButton(toolbar_radio, text=constants.lang['radio_cipher'], height=24,
                                            corner_radius=10, command=lambda: radio_select(2),
                                            fg_color=constants.theme['color']['deselected'][constants.mode],
                                            hover=False)
        radio_text_button.place(x=-10, y=0)
        radio_analysis_button.place(x=-10, y=24)
        radio_cipher_button.place(x=-10, y=48)
        radio_buttons = [radio_text_button, radio_analysis_button, radio_cipher_button]
        
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=toolbar_copy_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=15, command=copy_output).place(x=50, y=4)
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=toolbar_clear_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=15, command=clear_stages).place(x=84, y=4)
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=toolbar_increase_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=15, command=lambda: change_font_size(2)).place(x=50, y=38)
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=toolbar_decrease_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=15, command=lambda: change_font_size(-2)).place(x=84, y=38)
        ctk.CTkButton(toolbar_menu, text='', width=44, height=44, image=toolbar_theme_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=22, command=swap_theme).place(x=122, y=14)
        ctk.CTkButton(toolbar_menu, text='', width=44, height=44, image=toolbar_options_image,
                      fg_color=constants.theme['color']['deselected'][constants.mode],
                      hover_color=constants.theme['color']['button'][constants.mode],
                      corner_radius=22).place(x=174, y=14)
        stages_canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0, width=210)
        stages_canvas.columnconfigure(0, weight=1)
        stages_canvas.grid(row=3, column=1, sticky='NESW')
        stages_canvas.bind('<MouseWheel>', stage_scroll)
        stages_canvas.create_rectangle(196, 0, 196, 0,
                                       outline=constants.theme['color']['deselected'][constants.mode])
        stage_frame = ctk.CTkFrame(root, fg_color=named_to_hex(constants.theme['color']['entry'][constants.mode]))
        stage_frame.grid(row=2, column=0, rowspan=2, sticky='NESW')
        stage_frame.grid_propagate(0)
        loading_animation_label = ctk.CTkLabel(stage_frame)
        output_frame = ctk.CTkFrame(root, fg_color=named_to_hex(constants.theme['color']['entry'][constants.mode]))
        output_frame.grid(row=2, column=2, rowspan=2, sticky='NESW')
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.grid_propagate(0)
        stage_output = tk.Text(output_frame, bd=0, state='disabled',
                               bg=constants.theme['color']['entry'][constants.mode],
                               font=(constants.theme['text'][constants.os]['font'], font_size),
                               fg=constants.theme['color']['text'][constants.mode],
                               insertbackground=constants.theme['color']['text'][constants.mode])
        stage_output.grid(padx=8, pady=8, sticky='NESW')

        ctk.CTkButton(root, text='', image=toolbar_toggle_image,
                      width=42, height=30, fg_color=bg_color,
                      hover_color=adjust(bg_color, -20),
                      command=toggle_toolbar).grid(row=1, column=0, padx=5, pady=5, sticky='W')
        ctk.CTkLabel(root, text=constants.lang['stage_content']).grid(row=1, column=0)
        ctk.CTkLabel(root, text=constants.lang['stage_list']).grid(row=1, column=1)
        ctk.CTkLabel(root, text=constants.lang['output']).grid(row=1, column=2)
        root.update()
        
        results = {}
        max_result = ''
        old_current_stages = current_stages.copy()
        old_stage_positions = stage_positions.copy()
        current_stages = []
        stage_positions = {}
        for stage in old_stage_positions.values():
            stage = old_current_stages[stage]
            add_stage(0, type(stage[0]).__name__, stage[0], update=False)

        if selected_stage >= 0 and len(stage_positions) != 0:
            index = selected_stage
            switch_stage(index, unselect=False)

        root.update()
        stage_scroll(None)

    def update_window():
        global stage_up_image, stage_down_image, toolbar_options_image, toolbar_clear_image
        global stage_hidden_image, stage_remove_image, toolbar_active, toolbar_separator_image
        global toolbar_increase_image, toolbar_decrease_image, toolbar_copy_image, font_size
        global toolbar_theme_image, toolbar_stage_image, stage_shown_image, loading_animation_images
        global icon_image, toolbar_toggle_image

        constants.load_constants()
        if not font_size: font_size = constants.theme['text'][constants.os]['size']
        
        icon_image = tk.PhotoImage(file=constants.theme['path']['window_icon'])
        toolbar_toggle_image = tk.PhotoImage(file=constants.theme['path']['toolbar_icon'])
        stage_up_image = tk.PhotoImage(file=constants.theme['path']['stage_up'][constants.mode])
        stage_down_image = tk.PhotoImage(file=constants.theme['path']['stage_down'][constants.mode])
        stage_remove_image = tk.PhotoImage(file=constants.theme['path']['stage_remove'])
        stage_shown_image = tk.PhotoImage(file=constants.theme['path']['stage_shown'])
        stage_hidden_image = tk.PhotoImage(file=constants.theme['path']['stage_hidden'])
        toolbar_separator_image = tk.PhotoImage(file=constants.theme['path']['toolbar_separator'])
        toolbar_stage_image = tk.PhotoImage(file=constants.theme['path']['toolbar_stage'][constants.mode])
        toolbar_increase_image = tk.PhotoImage(file=constants.theme['path']['toolbar_increase'][constants.mode])
        toolbar_decrease_image = tk.PhotoImage(file=constants.theme['path']['toolbar_decrease'][constants.mode])
        toolbar_copy_image = tk.PhotoImage(file=constants.theme['path']['toolbar_copy'][constants.mode])
        toolbar_clear_image = tk.PhotoImage(file=constants.theme['path']['toolbar_clear'][constants.mode])
        toolbar_theme_image = tk.PhotoImage(file=constants.theme['path']['toolbar_theme'][constants.mode])
        toolbar_options_image = tk.PhotoImage(file=constants.theme['path']['toolbar_options'][constants.mode])
        loading_animation_images = [tk.PhotoImage(file=constants.theme['path']['loading_animation'][constants.mode],
                                                  format=f'gif -index {x}') for x in range(8)]
        root.iconphoto(False, icon_image)
        root.title(constants.lang['title'])

        ctk.set_appearance_mode(constants.mode_name)
        ctk.set_default_color_theme(constants.theme_path + constants.theme_name + '.json')    
        for widget in root.winfo_children():
            widget.destroy()
        create_widgets()

        if toolbar_active:
            toolbar_active = False
            toggle_toolbar()
        radio_select(radio_selected)

    def check_darkdetect_queue():
        try:
            darkdetect_queue.get(False)
            if constants.mode_name == 'default':
                update_window()
        except:
            pass
        root.after(constants.check_queue_delay, check_darkdetect_queue)

    def toolbar_animation(toolbar_active, start, stop, step, delay):
        global toolbar_animated

        toolbar.config(height=start, width=root.winfo_width())
        if (start != 0 and start != 72
            and start % 72 / constants.toolbar_step // (constants.toolbar_updates
                                                        + 1) * constants.toolbar_step == 0):
            root.update()
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
                toolbar_animation(toolbar_active, 0, 72, constants.toolbar_step, constants.toolbar_delay)
            else:
                toolbar_animated = True
                toolbar_animation(toolbar_active, 72, 0, -constants.toolbar_step, constants.toolbar_delay)
    
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
        global radio_selected, toolbar_stages, toolbar_stages_last
        bg_color = named_to_hex(constants.theme['color']['bg_color'][constants.mode])
        deselected_color = constants.theme['color']['deselected'][constants.mode]
        button_color = named_to_hex(constants.theme['color']['button'][constants.mode])
        
        radio_buttons[radio_selected].configure(fg_color=deselected_color, hover_color=deselected_color)
        radio_buttons[button].configure(fg_color=button_color, hover_color=named_to_hex)
        radio_selected = button
        
        for stage in toolbar_stages:
            toolbar_canvas.delete(stage[0])
            toolbar_canvas.delete(stage[1])
        toolbar_stages = []
        x = 0
        for stage in defined_stages[button]:
            x = 79 + 180 * (len(toolbar_stages) // 2)
            y = 19 + 36 * (len(toolbar_stages) % 2)
            
            image = toolbar_canvas.create_image(x, y, image=toolbar_stage_image)
            text = toolbar_canvas.create_text(x, y - 4, text=constants.lang['stage_' + stage.lower()]['name'],
                                         font=(constants.theme['text'][constants.os]['font'],
                                               constants.theme['text'][constants.os]['size'] + 2),
                                         fill=constants.theme['color']['text'][constants.mode])
            for item in [image, text]:
                toolbar_canvas.tag_bind(item, '<Button-1>', lambda event, stage=stage: add_stage(button, stage))
                toolbar_canvas.tag_bind(item, '<Enter>', lambda event: toolbar_canvas.config(cursor='hand2'))
                toolbar_canvas.tag_bind(item, '<Leave>', lambda event: toolbar_canvas.config(cursor=''))
            toolbar_stages.append((image, text))

        toolbar_stages_last = x + 75
        start, end = cal_scrollbar(toolbar_canvas.winfo_width(), toolbar_stages_last, toolbar_stages_pos)
        toolbar_canvas.coords(1, start, 0, end, 0)
        
    def toolbar_scroll(event):
        global toolbar_stages_pos

        if event: new_pos = toolbar_stages_pos + event.delta // 3
        else: new_pos = toolbar_stages_pos
        new_pos = max(new_pos, 0)
        new_pos = min(new_pos, max(toolbar_stages_last - toolbar_canvas.winfo_width(), 0))
        
        for widget in toolbar_canvas.find_all()[1:]:
            toolbar_canvas.move(widget, toolbar_stages_pos - new_pos, 0)
        toolbar_stages_pos = new_pos
        start, end = cal_scrollbar(toolbar_canvas.winfo_width(), toolbar_stages_last, toolbar_stages_pos)
        toolbar_canvas.coords(1, start, 0, end, 0)

    def stage_scroll(event):
        global stages_pos

        if event: new_pos = stages_pos - event.delta // 3
        else: new_pos = stages_pos
        new_pos = max(new_pos, 0)
        new_pos = min(new_pos, max(stages_last - stages_canvas.winfo_height(), 0))
        
        for widget in stages_canvas.find_all()[1:]:
            stages_canvas.move(widget, 0, stages_pos - new_pos)
        for widget in stages_canvas.winfo_children():
            widget.place(x=widget.winfo_x(), y=widget.winfo_y() + stages_pos - new_pos)
        stages_pos = new_pos
        start, end = cal_scrollbar(stages_canvas.winfo_height(), stages_last, stages_pos)
        stages_canvas.coords(1, 196, start, 196, end)

    def cal_scrollbar(width, maximum, pos):
        if maximum <= width:
            return (-1, -1)
        scrollbar_length = width / (maximum / width)
        scrollbar_distance = pos / (maximum - width) * (width - scrollbar_length)
        return (scrollbar_distance, scrollbar_distance + scrollbar_length)

    def create_stage(stage, stage_type):
        name = stage.__name__
        defined_stages[stage_type][name] = stage

    def add_stage(stage_type, name, stage=None, update=True):
        global max_result, stages_last
        
        length = len(stage_positions.keys())
        display_name = constants.lang['stage_' + name.lower()]['name']
        bg_color = named_to_hex(constants.theme['color']['bg_color'][constants.mode])
        y = (stage_up_image.height() + 4) * length + stage_up_image.height() // 2
        stages_last = max(stages_last, y + stage_up_image.height() // 2)
        y -= stages_pos
        image = stages_canvas.create_image(stages_canvas.winfo_width() // 2, y, image=stage_up_image)
        text = stages_canvas.create_text(stages_canvas.winfo_width() // 2, y - 4, text=display_name,
                                         font=(constants.theme['text'][constants.os]['font'],
                                               constants.theme['text'][constants.os]['size'] + 2),
                                         fill=constants.theme['color']['text'][constants.mode])
        
        if stage:
            stage.setup(stage_frame, constants.lang['stage_' + name.lower()])
        else:
            stage = defined_stages[stage_type][name](update_output)
            stage.setup(stage_frame, constants.lang['stage_' + name.lower()])

        for i, v in enumerate(current_stages):
            if not v:
                stage_index = i
                replace = True
                break
        else:
            stage_index = len(current_stages)
            replace = False
            
        stage_positions[length] = stage_index
        if not stage_index in stages_shown:
            stages_shown[stage_index] = True

        for item in [image, text]:
            stages_canvas.tag_bind(item, '<ButtonPress-1>', lambda event: stage_mb_down(event, stage_index))
            stages_canvas.tag_bind(item, '<ButtonRelease-1>', stage_mb_up)
            stages_canvas.tag_bind(item, '<Motion>', stage_mouse_move)
            stages_canvas.tag_bind(item, '<Enter>', lambda event: stages_canvas.config(cursor='hand2'))
            stages_canvas.tag_bind(item, '<Leave>', lambda event: stages_canvas.config(cursor=''))
            
        if name != 'Input':
            remove = ctk.CTkButton(stages_canvas, text='', image=stage_remove_image,
                   width=21, height=21, fg_color=bg_color,
                   hover_color=adjust(bg_color, -8),
                   command=lambda: remove_stage(stage_index))
            remove.place(x=stage_up_image.width() + 25, y=y - 9)
            if stages_shown[stage_index]:
                toggle_show = ctk.CTkButton(stages_canvas, text='', image=stage_shown_image,
                       width=21, height=21, fg_color=bg_color,
                       hover_color=adjust(bg_color, -8),
                       command=lambda: toggle_hidden(stage_index))
            else:
                toggle_show = ctk.CTkButton(stages_canvas, text='', image=stage_hidden_image,
                       width=21, height=21, fg_color=bg_color,
                       hover_color=adjust(bg_color, -8),
                       command=lambda: toggle_hidden(stage_index))
            toggle_show.place(x=3, y=y - 9)
        
        if name == 'Input':
            results[stage_index] = stage.input
            if replace:
                current_stages[stage_index] = (stage, image, text)
            else:
                current_stages.append((stage, image, text))
        else:
            if update:
                if constants.threaded:
                    returns = threaded_update([max_result, (stage.update, stage.update_vars, stage_type == 1)])
                else:
                    returns = unthreaded_update([max_result, (stage.update, stage.update_vars, stage_type == 1)])
                if stage_type != 1:
                    results[stage_index] = returns[0][0]
                    stage.update_widgets(*returns[0][1])
                else:
                    stage.update_widgets(*returns[0])
            if replace:
                current_stages[stage_index] = [stage, image, text, remove, toggle_show]
            else:
                current_stages.append([stage, image, text, remove, toggle_show])

        if stage_type != 1 and update:
            max_result = results[stage_index]
            set_output(max_result)
        if update:
            root.update()
            stage_scroll(None)

    def remove_stage(stage_index, update=True):
        global stages_last
        
        stage = current_stages[stage_index]
        pos_index = next(k for k, v in stage_positions.items() if v == stage_index)
        
        current_stages[stage_index] = None
        del stage_positions[pos_index]
        del stages_shown[stage_index]
        stages_canvas.delete(stage[1])
        stages_canvas.delete(stage[2])
        stage[3].destroy()
        stage[4].destroy()
        move_stages(pos_index + 1, len(stage_positions), -1)
        stages_last -= stage_up_image.height() + 4

        if selected_stage == stage_index:
            if pos_index == len(stage_positions):
                switch_stage(stage_positions[len(stage_positions) - 1], unselect=False)
            else:
                switch_stage(stage_positions[pos_index], unselect=False)
        remove_result(stage_index, pos_index, update=update)

        if update:
            root.update()
            stage_scroll(None)

    def move_stages(range_start, range_end, amount):
        global stages_last
        
        for i in range(range_start, range_end + 1):
            stage = current_stages[stage_positions[i]]
            y = (stage_up_image.height() + 4) * (i + amount) + stage_up_image.height() // 2
            stages_last = max(stages_last, y + stage_up_image.height() // 2)
            y -= stages_pos

            if stage_positions[i] == selected_stage:
                stages_canvas.coords(stage[2], stages_canvas.coords(stage[1])[0], y)
            else:
                stages_canvas.coords(stage[2], stages_canvas.coords(stage[1])[0], y - 4)
            stages_canvas.coords(stage[1], stages_canvas.coords(stage[1])[0], y)
            stage[3].place(x=stage_up_image.width() + 25, y=y - 9)
            stage[4].place(x=3, y=y - 9)

            if amount != 0:
                stage_positions[i + amount] = stage_positions[i]
                del stage_positions[i]

    def toggle_hidden(stage_index):
        stage = current_stages[stage_index]
        analysis = bool([True for x in defined_stages[1] if isinstance(stage[0], defined_stages[1][x])])
        pos_index = next(k for k, v in stage_positions.items() if v == stage_index)
        if stages_shown[stage_index]:
            stage[4].configure(image=stage_hidden_image)
            stages_shown[stage_index] = False
            if not analysis:
                remove_result(stage_index, pos_index)
        else:
            stage[4].configure(image=stage_shown_image)
            stages_shown[stage_index] = True
            if not analysis:
                results[stage_index] = ''
                update_output(stage[0])

    def remove_result(stage_index, pos_index, update=True):
        global max_result
        
        if stage_index in results:
            del results[stage_index]
        if pos_index != len(stage_positions) and update:
            update_output(current_stages[stage_positions[pos_index]][0])
        else:
            max_result = results[next(v for k, v in reversed(stage_positions.items()) if v in results)]
            set_output(max_result)

    def switch_stage(index, unselect=True):
        global selected_stage, stage_frame

        selected = current_stages[index]
        
        if selected_stage != index or not unselect:
            stages_canvas.itemconfigure(selected[1], image=stage_down_image)
            stages_canvas.move(selected[2], 0, 4)
            if unselect:
                old_selected = current_stages[selected_stage]
                stages_canvas.itemconfigure(old_selected[1], image=stage_up_image)
                stages_canvas.move(old_selected[2], 0, -4)
            selected_stage = index

            for widget in stage_frame.winfo_children():
                widget.grid_forget()
            for i in range(0, 10):
                stage_frame.rowconfigure(i, weight=0)
                stage_frame.columnconfigure(i, weight=0)
            selected[0].display()
            stages_canvas.focus_set()

    def stage_mouse_move(event):
        global dragged_end
        global dragging
        global dragged_stage_pos_start
        global stage_positions

        if dragging:
            stage = current_stages[dragged_stage]
            x = stages_canvas.coords(stage[1])[0]

            stage[3].place(x=stage_up_image.width() + 25, y=event.y - 9)
            stage[4].place(x=3, y=event.y - 9)
            stages_canvas.coords(stage[1], x, event.y)
            if dragged_stage == selected_stage:
                stages_canvas.coords(stage[2], x, event.y)
            else:
                stages_canvas.coords(stage[2], x, event.y - 4)

            pos_index = next(k for k, v in stage_positions.items() if v == dragged_stage)
            y = (stage_up_image.height() + 4) * pos_index + stage_up_image.height() // 2 - stages_pos
            difference = event.y - y
            if difference != 0:
                direction = int(difference / abs(difference))
                move_stage = pos_index + direction
                
                if (abs(difference) > stage_up_image.height() // 2 + 4 and
                    move_stage != 0 and move_stage < len(stage_positions)):
                    move_stages(move_stage, move_stage, 0 - direction)
                    stage_positions[pos_index + direction] = dragged_stage
                    stage_positions = dict(sorted(stage_positions.items()))
            
        elif dragged_stage > 0:
            dragged_end = (event.x, event.y)
            movement = max(abs(dragged_start[0] - dragged_end[0]), abs(dragged_start[1] - dragged_end[1]))
            if movement > constants.stages_drag_max:
                stage = current_stages[dragged_stage]
                stages_canvas.tag_raise(stage[1])
                stages_canvas.tag_raise(stage[2])
                items = stages_canvas.find_all()
                stage[2] = items[-1]
                stage[1] = items[-2]
                dragged_stage_pos_start = next(k for k, v in stage_positions.items() if v == dragged_stage)
                dragging = True
    
    def stage_mb_down(event, index):
        global dragged_stage
        global dragged_start
        global dragged_end
        
        dragged_stage = index
        dragged_start = (event.x, event.y)
        dragged_end = (event.x, event.y)

    def stage_mb_up(event):
        global dragged_stage
        global dragging
        global dragged_stage_pos_start
        
        movement = max(abs(dragged_start[0] - dragged_end[0]), abs(dragged_start[1] - dragged_end[1]))
        if dragging:
            pos_index = next(k for k, v in stage_positions.items() if v == dragged_stage)
            update_output(current_stages[stage_positions[min(pos_index, dragged_stage_pos_start)]][0])
            move_stages(pos_index, pos_index, 0)
            dragging = False
            dragged_stage = -1
            
        elif dragged_stage > -1 and movement <= constants.stages_drag_max:
            switch_stage(dragged_stage)
            dragged_stage = -1

    def update_output(stage):
        global max_result, results

        start_stage_index = [i for i, v in enumerate(current_stages) if v and v[0] is stage][0]
        start_pos_index = next(k for k, v in stage_positions.items() if v == start_stage_index)
        updating_stages = []
        for i in range(start_pos_index, len(stage_positions)):
            stage_index = stage_positions[i]
            x = current_stages[stage_index]
            for y in defined_stages[0]:
                if isinstance(x[0], defined_stages[0][y]) and stages_shown[stage_index]:
                    updating_stages.append((stage_index, True))
                    break
            else:
                for y in defined_stages[1]:
                    if isinstance(x[0], defined_stages[1][y]) and stages_shown[stage_index]:
                        updating_stages.append((stage_index, False))
                        break
                else:
                    for y in defined_stages[2]:
                        if isinstance(x[0], defined_stages[2][y]) and stages_shown[stage_index]:
                            updating_stages.append((stage_index, True))
        if start_pos_index == 0:
            results[0] = current_stages[0][0].input
        if updating_stages:
            search_item = updating_stages[0][0]
            to_search = list(stage_positions.values())
            to_search = to_search[:to_search.index(search_item)]
            updating_stages.insert(0, ([x for x in to_search if x < search_item and x in results][-1], True))
            
            updates = [results[updating_stages[0][0]]]
            for i, v in enumerate(updating_stages[1:]):
                function = current_stages[v[0]][0].update
                args = current_stages[v[0]][0].update_vars
                if v[1]: analysis = False
                else: analysis = True
                updates.append((function, args, analysis))
            if constants.threaded:
                returns = threaded_update(updates)
            else:
                returns = unthreaded_update(updates)
            for i, v in enumerate(updating_stages[1:]):
                if v[1]:
                    results[v[0]] = returns[i][0]
                    current_stages[v[0]][0].update_widgets(*returns[i][1])
                else:
                    current_stages[v[0]][0].update_widgets(*returns[i])
            
        max_result = results[next(v for k, v in reversed(stage_positions.items()) if v in results)]
        set_output(max_result)

    def threaded_update(updates):
        global loading

        loading = True
        root.after(400, start_loading_animation, 0, True)
        update_queue_in.put(updates)
        while True:
            if update_queue_out.empty():
                root.update()
                root.update_idletasks()
                time.sleep(constants.loading_delay / 1000)
            else:
                returns = update_queue_out.get()
                break
        loading = False
        
        return returns

    def unthreaded_update(updates):
        text = updates.pop(0)
        returns = []
        for update in updates:
            function, args, analysis = update
            result = function(text, *args)
            returns.append(result)
            if not analysis: text = result[0]

        return returns

    def start_loading_animation(frame, start=False):
        global loading

        if start == True and loading:
            stage_frame.grab_set()
            for widget in stage_frame.winfo_children():
                if widget != loading_animation_label:
                    widget.grid_forget()
            loading_animation_label.grid()
            start_loading_animation(frame)
        elif loading:
            loading_animation_label.configure(image=loading_animation_images[frame])
            root.after(100, start_loading_animation, (frame + 1) % 8)
        else:
            stage_frame.grab_release()
            loading_animation_label.grid_forget()
            current_stages[selected_stage][0].display()
    
    def copy_output():
        root.clipboard_clear()
        root.clipboard_append(max_result)
        root.update()

    def clear_stages():
        for i, v in enumerate(current_stages[1:]):
            if v:
                remove_stage(i + 1, update=False)
        root.update()
        stage_scroll(None)
        current_stages[0][0].input_widget.delete(1.0, 'end')

    def change_font_size(amount):
        global font_size
        
        font_size = max(min(font_size - amount, -9), -21)
        current_stages[0][0].input_widget.configure(font=(constants.theme['text'][constants.os]['font'],
                                                          font_size))
        stage_output.configure(font=(constants.theme['text'][constants.os]['font'], font_size))

    def swap_theme():
        global constants_name

        if not toolbar_animated:
            if constants.mode == 0: constants.mode_name = 'dark'
            elif constants.mode == 1: constants.mode_name = 'light'

            update_window()

    root = ctk.CTk()
    if constants.threaded:
        darkdetect_queue = multiprocessing.Queue()
        x = multiprocessing.Process(target=darkdetect.listener, args=(darkdetect_queue.put,))
        x.daemon = True
        x.start()
        update_queue_in = multiprocessing.Queue()
        update_queue_out = multiprocessing.Queue()
        y = multiprocessing.Process(target=output_thread, args=(update_queue_in, update_queue_out))
        y.daemon = True
        y.start()
    toolbar_active = False
    toolbar_animated = False
    toolbar_stages_last = 0
    stages_last = 0
    font_size = 0
    dragging = False
    dragged_start = (0, 0)
    dragged_end = (0, 0)
    dragged_stage_pos_start = 0
    radio_selected = 0
    selected_stage = 0
    defined_stages = [{}, {}, {}]
    current_stages = []
    stage_positions = {}
    stages_shown = {}
    toolbar_stages = []

    root.geometry(constants.default_size)
    root.bind('<Configure>', resize)
    root.minsize(int(constants.min_size.split('x')[0]), int(constants.min_size.split('x')[1]))
    root.columnconfigure(0, weight=1)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(2, minsize=35)
    root.rowconfigure(3, weight=1)

    create_stage(UpperCase, 0)
    create_stage(LowerCase, 0)
    create_stage(Reverse, 0)
    create_stage(Strip, 0)
    create_stage(Block, 0)
    create_stage(Spaces, 0)

    create_stage(Length, 1)
    create_stage(Frequency, 1)
    create_stage(IoC, 1)
    
    check_darkdetect_queue()
    update_window()

    add_stage(0, 'Input', Input(update_output))
    switch_stage(0, unselect=False)
    
    root.mainloop()

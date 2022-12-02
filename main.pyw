def output_thread(queue_in, queue_out):
    cached_constants = None
    while True:
        updates = queue_in.get()
        text, constants = updates.pop(0)
        if constants:
            cached_constants = constants
        returns = []
        for update in updates:
            function, args, analysis = update
            result = function(text, cached_constants, *args)
            returns.append(result)
            if not analysis: text = result[0]
        queue_out.put(returns)

from stages_text import *
from stages_analysis import *
from stages_cipher import *
from defined import Stage, Constants
from PIL import Image
import tkinter as tk
import customtkinter as ctk
import sys
import multiprocessing
import darkdetect
import importlib
import json
import time

class Input(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.input = ''

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        mode = constants.mode
        bg_color = constants.theme['CTkEntry']['fg_color'][mode]
        text_color = constants.theme['CTkLabel']['text_color'][mode]

        self.input_widget = tk.Text(frame, bg=bg_color, fg=text_color, bd=0,
                                    wrap='word', font=font, insertbackground=text_color)
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
    
class App():
    def __init__(self):
        self.toolbar_active = False
        self.toolbar_stages_last = 0
        self.stages_last = 0
        self.font_change_after = None
        self.dragging = False
        self.dragged_start = (0, 0)
        self.dragged_end = (0, 0)
        self.dragged_stage_pos_start = 0
        self.dragged_stage = -1
        self.radio_selected = 0
        self.selected_stage = 0
        self.defined_stages = [{}, {}, {}]
        self.current_stages = []
        self.stage_positions = {}
        self.stages_shown = {}
        self.toolbar_stages = []

        self.create_stage(UpperCase, 0)
        self.create_stage(LowerCase, 0)
        self.create_stage(Reverse, 0)
        self.create_stage(Strip, 0)
        self.create_stage(Block, 0)
        self.create_stage(Spaces, 0)

        self.create_stage(Length, 1)
        self.create_stage(Frequency, 1)
        self.create_stage(IoC, 1)
        self.create_stage(SubstitutionFinder, 1)

        self.create_stage(BinaryCode, 2)
        self.create_stage(Caesar, 2)
        self.create_stage(Affine, 2)
        self.create_stage(Substitution, 2)
        self.create_stage(Vigenere, 2)

    def start(self):
        self.root = ctk.CTk()
        self.constants = Constants()

        self.root.geometry(self.constants.default_size)
        self.root.bind('<Configure>', self.resize)
        self.root.minsize(int(self.constants.min_size.split('x')[0]),
                          int(self.constants.min_size.split('x')[1]))
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(2, minsize=35)
        self.root.rowconfigure(3, weight=1)

        if self.constants.threaded:
            darkdetect_queue = multiprocessing.Queue()
            x = multiprocessing.Process(target=darkdetect.listener, args=(darkdetect_queue.put,))
            x.daemon = True
            x.start()
            self.update_queue_in = multiprocessing.Queue()
            self.update_queue_out = multiprocessing.Queue()
            y = multiprocessing.Process(target=output_thread, args=(self.update_queue_in,
                                                                    self.update_queue_out))
            y.daemon = True
            y.start()

        self.check_darkdetect_queue()
        self.update_window()

        self.add_stage(0, 'Input', Input(self.update_output))
        self.switch_stage(0, unselect=False)
        if self.constants.threaded:
            self.threaded_update([('', self.constants)])

        self.root.mainloop()

    def update_window(self): 
        self.constants.load()
        self.update_constants = True 

        text = self.constants.theme['CTkFont'][self.constants.os]
        paths = self.constants.theme['Path']
        mode = self.constants.mode
        lang = self.constants.lang
        
        icon_image = tk.PhotoImage(file=paths['window_icon'])
        self.stage_up_image = tk.PhotoImage(file=paths['stage_up'][mode])
        self.stage_down_image = tk.PhotoImage(file=paths['stage_down'][mode])
        self.toolbar_stage_image = tk.PhotoImage(file=paths['toolbar_stage'][mode])
        
        self.toolbar_toggle_image = self.load_image('toolbar_icon', False)
        self.stage_remove_image = self.load_image('stage_remove', False)
        self.stage_shown_image = self.load_image('stage_shown', False)
        self.stage_hidden_image = self.load_image('stage_hidden', False)
        self.toolbar_separator_image = self.load_image('toolbar_separator', False)
        self.toolbar_increase_image = self.load_image('toolbar_increase', True)
        self.toolbar_decrease_image = self.load_image('toolbar_decrease', True)
        self.toolbar_copy_image = self.load_image('toolbar_copy', True)
        self.toolbar_clear_image = self.load_image('toolbar_clear', True)
        self.toolbar_theme_image = self.load_image('toolbar_theme', True)
        self.toolbar_options_image = self.load_image('toolbar_options', True)

        loading_animation_obj = Image.open(paths['loading_animation'][mode])
        self.loading_animation_images = []
        for i in range(0, 8):
            loading_animation_obj.seek(i)
            frame = Image.new("RGBA", loading_animation_obj.size)
            frame.paste(loading_animation_obj)
            self.loading_animation_images.append(ctk.CTkImage(light_image=frame,
                                                              size=loading_animation_obj.size))
            
        self.root.iconphoto(False, icon_image)
        self.root.title(lang['title'])
        
        self.display_font = ctk.CTkFont(family=text['family'], size=text['size'])
        self.custom_font = ctk.CTkFont(family=text['family'], size=text['size'])
        self.stage_font = ctk.CTkFont(family=text['family'], size=text['size'] - 2)
        ctk.set_appearance_mode(self.constants.mode_name)
        self.toolbar_animated = False
        ctk.set_default_color_theme(self.constants.theme_path + self.constants.theme_name + '.json')    
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
        
        if self.toolbar_active:
            self.toolbar_active = False
            self.toggle_toolbar()
        self.radio_select(self.radio_selected)

    def create_widgets(self):
        def enter_button(button):
            button.configure(cursor='hand2')
            button.configure(fg_color=theme['CTkButton']['fg_color'][mode])
        def leave_button(button):
            button.configure(cursor='')
            button.configure(fg_color=deselected)

        theme = self.constants.theme
        mode = self.constants.mode
        lang = self.constants.lang
        named_to_hex = self.constants.named_to_hex

        self.toolbar_stages_pos = 0
        self.stages_pos = 0
        self.loading = False
        self.font_size_held = False
        root = self.root
        bg_color = named_to_hex(theme['CTk']['fg_color'][mode], root)

        self.toolbar = ctk.CTkFrame(self.root, fg_color=bg_color)
        self.toolbar.grid_propagate(0)
        self.toolbar.columnconfigure(1, weight=1)
        toolbar_radio = ctk.CTkFrame(self.toolbar, fg_color=bg_color, width=180)
        toolbar_radio.grid(row=0, column=0, sticky='NE')
        toolbar_radio.grid(row=0, column=0, sticky='NE')
        toolbar_menu = ctk.CTkFrame(self.toolbar, fg_color=bg_color, width=250)
        toolbar_menu.grid(row=0, column=2, sticky='NW')
        self.toolbar_canvas = tk.Canvas(self.toolbar, bg=bg_color, highlightthickness=0)
        self.toolbar_canvas.grid(row=0, column=1, sticky='EW')
        self.toolbar_canvas.bind('<MouseWheel>', self.toolbar_scroll)

        self.toolbar_canvas.create_rectangle(0, 0, 0, 0, outline=theme['Custom']['deselected'][mode])
        ctk.CTkButton(toolbar_radio, fg_color='transparent', hover=False, text='',
                      image=self.toolbar_separator_image).place(x=85, y=0)
        ctk.CTkButton(toolbar_menu, fg_color='transparent', hover=False, text='',
                      image=self.toolbar_separator_image).place(x=-45, y=0)
        text_color = named_to_hex(theme['CTkLabel']['text_color'][mode], root)
        deselected = theme['Custom']['deselected'][mode]
        radio_text_button = ctk.CTkButton(toolbar_radio, text=lang['radio_text'], height=24,
                                          corner_radius=10, command=lambda: self.radio_select(0),
                                          fg_color=deselected, hover=False,
                                          text_color=text_color, font=self.custom_font)
        radio_analysis_button = ctk.CTkButton(toolbar_radio, text=lang['radio_analysis'], height=24,
                                              corner_radius=10, command=lambda: self.radio_select(1),
                                              fg_color=deselected, hover=False,
                                              text_color=text_color, font=self.custom_font)
        radio_cipher_button = ctk.CTkButton(toolbar_radio, text=lang['radio_cipher'], height=24,
                                            corner_radius=10, command=lambda: self.radio_select(2),
                                            fg_color=deselected, hover=False,
                                            text_color=text_color, font=self.custom_font)
        radio_text_button.place(x=-10, y=0)
        radio_analysis_button.place(x=-10, y=24)
        radio_cipher_button.place(x=-10, y=48)
        self.radio_buttons = [radio_text_button, radio_analysis_button, radio_cipher_button]
        
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=self.toolbar_copy_image,
                      fg_color=deselected, hover_color=theme['CTkButton']['fg_color'][mode],
                      corner_radius=15, command=self.copy_output).place(x=50, y=4)
        ctk.CTkButton(toolbar_menu, text='', width=30, height=30, image=self.toolbar_clear_image,
                      fg_color=deselected, hover_color=theme['CTkButton']['fg_color'][mode],
                      corner_radius=15, command=self.clear_stages).place(x=84, y=4)
        ctk.CTkButton(toolbar_menu, text='', width=44, height=44, image=self.toolbar_theme_image,
                      fg_color=deselected, hover_color=theme['CTkButton']['fg_color'][mode],
                      corner_radius=22, command=self.swap_theme).place(x=122, y=14)
        ctk.CTkButton(toolbar_menu, text='', width=44, height=44, image=self.toolbar_options_image,
                      fg_color=deselected, hover_color=theme['CTkButton']['fg_color'][mode],
                      corner_radius=22).place(x=174, y=14)

        font_increase = ctk.CTkButton(toolbar_menu, text='', width=30, height=30,
                                      image=self.toolbar_increase_image, corner_radius=15,
                                      fg_color=deselected,
                                      hover_color=theme['CTkButton']['fg_color'][mode])
        font_decrease = ctk.CTkButton(toolbar_menu, text='', width=30, height=30,
                                      image=self.toolbar_decrease_image, corner_radius=15,
                                      fg_color=deselected,
                                      hover_color=theme['CTkButton']['fg_color'][mode])
        font_increase.place(x=50, y=38)
        font_decrease.place(x=84, y=38)
        
        for index, button in enumerate([font_increase, font_decrease]):
            for widget in [button._canvas, button._image_label]:
                widget.bind('<Enter>', lambda event, widget=button: enter_button(widget))
                widget.bind('<Leave>', lambda event, widget=button: leave_button(widget))
                widget.bind('<ButtonPress-1>', lambda event, index=index: self.font_size_down(-1 + index * 2))
                widget.bind('<ButtonRelease-1>', self.font_size_up)

        entry_color = theme['CTkEntry']['fg_color'][mode]
        self.stages_canvas = tk.Canvas(self.root, bg=bg_color, highlightthickness=0, width=230)
        self.stages_canvas.columnconfigure(0, weight=1)
        self.stages_canvas.grid(row=3, column=1, sticky='NESW')
        self.stages_canvas.bind('<MouseWheel>', self.stage_scroll)
        self.stages_canvas.create_rectangle(225, 0, 225, 0, outline=deselected)
        self.stage_frame = ctk.CTkFrame(self.root, fg_color=entry_color)
        self.stage_frame.grid(row=2, column=0, rowspan=2, sticky='NESW')
        self.stage_frame.grid_propagate(0)
        self.loading_animation_label = ctk.CTkLabel(self.stage_frame, text='')
        output_frame = ctk.CTkFrame(self.root, fg_color=entry_color)
        output_frame.grid(row=2, column=2, rowspan=2, sticky='NESW')
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.grid_propagate(0)
        self.stage_output = tk.Text(output_frame, bd=0, state='disabled', bg=entry_color,
                               font=self.display_font, fg=text_color, wrap='word',
                               insertbackground=text_color)
        self.stage_output.grid(padx=8, pady=8, sticky='NESW')

        ctk.CTkButton(self.root, text='', image=self.toolbar_toggle_image, width=42, height=30,
                      fg_color=bg_color, hover_color=self.adjust(bg_color, -20),
                      command=self.toggle_toolbar).grid(row=1, column=0, padx=5, pady=5, sticky='W')
        ctk.CTkLabel(self.root, text=lang['stage_content'],
                     font=self.custom_font).grid(row=1, column=0)
        ctk.CTkLabel(self.root, text=lang['stage_list'],
                     font=self.custom_font).grid(row=1, column=1)
        ctk.CTkLabel(self.root, text=lang['output'],
                     font=self.custom_font).grid(row=1, column=2)

        self.root.update()
        self.results = {}
        self.max_result = ''
        old_current_stages = self.current_stages.copy()
        old_stage_positions = self.stage_positions.copy()
        self.current_stages = []
        self.stage_positions = {}
        for stage in old_stage_positions.values():
            stage = old_current_stages[stage]
            self.add_stage(0, type(stage[0]).__name__, stage[0], update=False)

        if self.selected_stage >= 0 and len(self.stage_positions) != 0:
            self.switch_stage(self.selected_stage, unselect=False)

        self.root.update()
        self.stage_scroll(None)

    def create_stage(self, stage, stage_type):
        name = stage.__name__
        self.defined_stages[stage_type][stage.__name__] = stage

    def resize(self, event):
        if isinstance(event.widget, ctk.windows.ctk_tk.CTk) and not self.toolbar_animated:
            if self.toolbar_active:
                self.toolbar.configure(height=72, width=event.width)
            else: self.toolbar.configure(height=0, width=event.width)

        elif event.widget == self.toolbar_canvas:
            self.toolbar_scroll(None)
        elif event.widget is self.stages_canvas:
            self.stage_scroll(None)

    def toolbar_scroll(self, event):
        if event: new_pos = self.toolbar_stages_pos + event.delta // 3
        else: new_pos = self.toolbar_stages_pos
        new_pos = max(new_pos, 0)
        new_pos = min(new_pos, max(self.toolbar_stages_last - self.toolbar_canvas.winfo_width(), 0))
        
        for widget in self.toolbar_canvas.find_all()[1:]:
            self.toolbar_canvas.move(widget, self.toolbar_stages_pos - new_pos, 0)
        self.toolbar_stages_pos = new_pos
        start, end = self.cal_scrollbar(self.toolbar_canvas.winfo_width(), self.toolbar_stages_last,
                                        self.toolbar_stages_pos)
        self.toolbar_canvas.coords(1, start, 0, end, 0)

    def stage_scroll(self, event):
        if event: new_pos = self.stages_pos - event.delta // 3
        else: new_pos = self.stages_pos
        new_pos = max(new_pos, 0)
        new_pos = min(new_pos, max(self.stages_last - self.stages_canvas.winfo_height(), 0))
        
        for widget in self.stages_canvas.find_all()[1:]:
            self.stages_canvas.move(widget, 0, self.stages_pos - new_pos)
        for widget in self.stages_canvas.winfo_children():
            widget.place(x=widget.winfo_x(), y=widget.winfo_y() + self.stages_pos - new_pos)
        self.stages_pos = new_pos
        start, end = self.cal_scrollbar(self.stages_canvas.winfo_height(), self.stages_last,
                                        self.stages_pos)

        self.stages_canvas.coords(1, 225, start, 225, end)

    def cal_scrollbar(self, width, maximum, pos):
        if maximum <= width:
            return (-1, -1)
        scrollbar_length = width / (maximum / width)
        scrollbar_distance = pos / (maximum - width) * (width - scrollbar_length)

        return (scrollbar_distance, scrollbar_distance + scrollbar_length)

    def check_darkdetect_queue(self):
        try:
            self.darkdetect_queue.get(False)
            if self.constants.mode_name == 'default':
                self.update_window()
        except:
            pass

        self.root.after(self.constants.check_queue_delay, self.check_darkdetect_queue)

    def load_image(self, name, mode):
        path = self.constants.theme['Path'][name]
        if mode:
            path = path[self.constants.mode]
        image = Image.open(path)

        return ctk.CTkImage(light_image=image, size=image.size)

    def adjust(self, color, amount):
        new_hex = '#'
        for i in range(2, 8, 2):
            adjusted = int(color[i - 1:i + 1], 16) + amount
            new_hex += format(min(max(adjusted, 0), 255), '02X')
            
        return new_hex

    def copy_output(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.max_result)
        self.root.update()

    def clear_stages(self):
        for i, v in enumerate(self.current_stages[1:]):
            if v:
                self.remove_stage(i + 1, update=False)
        self.root.update()
        self.stage_scroll(None)
        self.current_stages[0][0].input_widget.delete(1.0, 'end')
        self.display_font.configure(size=self.custom_font.cget('size'))

    def font_size_down(self, amount):
        font_size = self.display_font.cget('size')
        font_size = min(max(font_size - amount, 9), 21)
        self.display_font.configure(size=font_size)

        self.font_size_after = self.root.after(self.constants.font_change_delay,
                                               lambda: self.font_size_down(amount))

    def font_size_up(self, event):
        self.root.after_cancel(self.font_size_after)
        self.font_size_held = False

    def swap_theme(self):
        if not self.toolbar_animated:
            if self.constants.mode == 0: self.constants.mode_name = 'dark'
            elif self.constants.mode == 1: self.constants.mode_name = 'light'

            self.update_window()

    def radio_select(self, button):
        theme = self.constants.theme
        mode = self.constants.mode
        button_color = theme['CTkButton']['fg_color'][mode]
        deselected = theme['Custom']['deselected'][mode]
        
        self.radio_buttons[self.radio_selected].configure(fg_color=deselected,
                                                          hover_color=deselected)
        self.radio_buttons[button].configure(fg_color=button_color)
        self.radio_selected = button
        
        for stage in self.toolbar_stages:
            self.toolbar_canvas.delete(stage[0])
            self.toolbar_canvas.delete(stage[1])

        self.toolbar_stages = []
        x = 0
        for stage in self.defined_stages[button]:
            x = 89 + 200 * (len(self.toolbar_stages) // 2)
            y = 19 + 36 * (len(self.toolbar_stages) % 2)
            
            name = self.constants.lang['stage_' + stage.lower()]['name']
            image = self.toolbar_canvas.create_image(x, y, image=self.toolbar_stage_image)
            text = self.toolbar_canvas.create_text(x, y - 4, font=self.stage_font, text=name,
                                                   fill=theme['CTkLabel']['text_color'][mode])
            
            enter = lambda event: self.toolbar_canvas.configure(cursor='hand2')
            exit_ = lambda event: self.toolbar_canvas.configure(cursor='')
            for item in [image, text]:
                add_command = lambda event, stage=stage: self.add_stage(button, stage)
                self.toolbar_canvas.tag_bind(item, '<Button-1>', add_command)
                self.toolbar_canvas.tag_bind(item, '<Enter>', enter)
                self.toolbar_canvas.tag_bind(item, '<Leave>', exit_)
            self.toolbar_stages.append((image, text))

        self.toolbar_stages_last = x + 75
        start, end = self.cal_scrollbar(self.toolbar_canvas.winfo_width(), self.toolbar_stages_last,
                                   self.toolbar_stages_pos)
        self.toolbar_canvas.coords(1, start, 0, end, 0)
    
    def switch_stage(self, index, unselect=True):
        selected = self.current_stages[index]
        
        if self.selected_stage != index or not unselect:
            self.stages_canvas.itemconfigure(selected[1], image=self.stage_down_image)
            self.stages_canvas.move(selected[2], 0, 4)
            if unselect:
                old_selected = self.current_stages[self.selected_stage]
                self.stages_canvas.itemconfigure(old_selected[1], image=self.stage_up_image)
                self.stages_canvas.move(old_selected[2], 0, -4)
            self.selected_stage = index

            for widget in self.stage_frame.winfo_children():
                widget.grid_forget()
            for i in range(0, 10):
                self.stage_frame.rowconfigure(i, weight=0, minsize=0)
                self.stage_frame.columnconfigure(i, weight=0, minsize=0)
            selected[0].display()
            self.stage_frame.focus_set()

    def set_output(self, text):
        self.stage_output.configure(state='normal')
        self.stage_output.delete(1.0, 'end')
        self.stage_output.insert(1.0, text)
        self.stage_output.configure(state='disabled')
        
    def toolbar_animation(self, toolbar_active, start, stop, step, delay):
        self.toolbar.configure(height=start, width=self.root.winfo_width())

        if (start != 0 and start != 72
            and start % 72 / self.constants.toolbar_step // (self.constants.toolbar_updates
                                                        + 1) * self.constants.toolbar_step == 0):
            self.root.update()
        if start * (step / abs(step)) < stop:
            self.toolbar.after(delay, self.toolbar_animation, toolbar_active,
                               start + step, stop, step, delay)

        else:
            if not self.toolbar_active:
                self.toolbar.place(x=0, y=-1)
            self.toolbar_animated = False

    def toggle_toolbar(self):
        if not self.toolbar_animated:
            self.toolbar_active = not self.toolbar_active
            if self.toolbar_active:
                self.toolbar.grid(row=0, column=0, columnspan=3)
                self.toolbar_animated = True
                self.toolbar_animation(self.toolbar_active, 0, 72, self.constants.toolbar_step,
                                       self.constants.toolbar_delay)

            else:
                self.toolbar_animated = True
                self.toolbar_animation(self.toolbar_active, 72, 0, -self.constants.toolbar_step,
                                       self.constants.toolbar_delay)

    def toggle_hidden(self, stage_index):
        stage = self.current_stages[stage_index]
        analysis = [True for x in self.defined_stages[1] if isinstance(stage[0],
                                                                       self.defined_stages[1][x])]
        analysis = bool(analysis)
        pos_index = next(k for k, v in self.stage_positions.items() if v == stage_index)

        if self.stages_shown[stage_index]:
            stage[4].configure(image=self.stage_hidden_image)
            stage[4]._update_image()
            self.stages_shown[stage_index] = False
            if not analysis:
                self.remove_result(stage_index, pos_index)
        else:
            stage[4].configure(image=self.stage_shown_image) 
            stage[4]._update_image()
            self.stages_shown[stage_index] = True
            if not analysis:
                self.results[stage_index] = ''
                self.update_output(stage[0])

    def stage_mb_down(self, event, index):
        self.dragged_stage = index
        self.dragged_start = (event.x, event.y)
        self.dragged_end = (event.x, event.y)

    def stage_mb_up(self, event):
        movement = max(abs(self.dragged_start[0] - self.dragged_end[0]),
                       abs(self.dragged_start[1] - self.dragged_end[1]))

        if self.dragging:
            pos_index = next(k for k, v in self.stage_positions.items() if v == self.dragged_stage)
            update = self.stage_positions[min(pos_index, self.dragged_stage_pos_start)]
            self.update_output(self.current_stages[update][0])
            self.move_stages(pos_index, pos_index, 0)
            self.dragging = False
            self.dragged_stage = -1
            
        elif self.dragged_stage > -1 and movement <= self.constants.stages_drag_max:
            self.switch_stage(self.dragged_stage)
            self.dragged_stage = -1

    def stage_mouse_move(self, event):
        if self.dragging:
            stage = self.current_stages[self.dragged_stage]
            x = self.stages_canvas.coords(stage[1])[0]

            stage[3].place(x=self.stage_up_image.width() + 25, y=event.y - 9)
            stage[4].place(x=3, y=event.y - 9)
            self.stages_canvas.coords(stage[1], x, event.y)
            if self.dragged_stage == self.selected_stage:
                self.stages_canvas.coords(stage[2], x, event.y)
            else:
                self.stages_canvas.coords(stage[2], x, event.y - 4)

            pos_index = next(k for k, v in self.stage_positions.items() if v == self.dragged_stage)
            y = 40 * pos_index + 36 // 2 - self.stages_pos
            difference = event.y - y
            if difference != 0:
                direction = int(difference / abs(difference))
                move_stage = pos_index + direction
                
                if (abs(difference) > 36 // 2 + 4 and move_stage != 0
                    and move_stage < len(self.stage_positions)):
                    self.move_stages(move_stage, move_stage, 0 - direction)
                    self.stage_positions[pos_index + direction] = self.dragged_stage
                    self.stage_positions = dict(sorted(self.stage_positions.items()))
            
        elif self.dragged_stage > 0:
            dragged_end = (event.x, event.y)
            movement = max(abs(self.dragged_start[0] - dragged_end[0]),
                           abs(self.dragged_start[1] - dragged_end[1]))
            if movement > self.constants.stages_drag_max:
                stage = self.current_stages[self.dragged_stage]
                self.stages_canvas.tag_raise(stage[1])
                self.stages_canvas.tag_raise(stage[2])
                items = self.stages_canvas.find_all()
                stage[2] = items[-1]
                stage[1] = items[-2]
                p_items = self.stage_positions.items()
                self.dragged_stage_pos_start = next(k for k, v in p_items if v == self.dragged_stage)
                self.dragging = True

    def add_stage(self, stage_type, name, stage=None, update=True):
        theme = self.constants.theme
        length = len(self.stage_positions.keys())
        display_name = self.constants.lang['stage_' + name.lower()]['name']
        bg_color = self.constants.named_to_hex(theme['CTk']['fg_color'][self.constants.mode],
                                               self.root)
        text_color = theme['CTkLabel']['text_color'][self.constants.mode]

        y = 40 * length + 36 // 2
        self.stages_last = max(self.stages_last, y + 36 // 2)
        y -= self.stages_pos
        image = self.stages_canvas.create_image(self.stages_canvas.winfo_width() // 2, y,
                                                image=self.stage_up_image)
        text = self.stages_canvas.create_text(self.stages_canvas.winfo_width() // 2, y - 4,
                                              text=display_name, font=self.stage_font,
                                              fill=text_color)
        
        for i, v in enumerate(self.current_stages):
            if not v:
                stage_index = i
                replace = True
                break
        else:
            stage_index = len(self.current_stages)
            replace = False
            
        self.stage_positions[length] = stage_index
        if not stage_index in self.stages_shown:
            self.stages_shown[stage_index] = True
        
        enter = lambda event: self.stages_canvas.configure(cursor='hand2')
        exit_ = lambda event: self.stages_canvas.configure(cursor='')
        for item in [image, text]:
            click_event = lambda event: self.stage_mb_down(event, stage_index)
            self.stages_canvas.tag_bind(item, '<ButtonPress-1>', click_event)
            self.stages_canvas.tag_bind(item, '<ButtonRelease-1>', self.stage_mb_up)
            self.stages_canvas.tag_bind(item, '<Motion>', self.stage_mouse_move)
            self.stages_canvas.tag_bind(item, '<Enter>', enter)
            self.stages_canvas.tag_bind(item, '<Leave>', exit_)
            
        if name != 'Input':
            if stage:
                stage.setup(self.stage_frame, self.constants, self.custom_font)
            else:
                stage = self.defined_stages[stage_type][name](self.update_output)
                stage.setup(self.stage_frame, self.constants, self.custom_font)
            remove = ctk.CTkButton(self.stages_canvas, text='', image=self.stage_remove_image,
                                   command=lambda: self.remove_stage(stage_index),
                                   width=21, height=21, fg_color=bg_color, 
                                   hover_color=self.adjust(bg_color, -8))
            remove.place(x=self.stage_up_image.width() + 25, y=y - 9)
            if self.stages_shown[stage_index]:
                toggle_show = ctk.CTkButton(self.stages_canvas, text='', height=21, width=21,
                                            fg_color=bg_color, image=self.stage_shown_image,
                                            hover_color=self.adjust(bg_color, -8),
                                            command=lambda: self.toggle_hidden(stage_index))
            else:
                toggle_show = ctk.CTkButton(self.stages_canvas, text='', height=21, width=21,
                                            fg_color=bg_color, image=self.stage_hidden_image,
                                            hover_color=self.adjust(bg_color, -8),
                                            command=lambda: self.toggle_hidden(stage_index))
            toggle_show.place(x=3, y=y - 9)
        
            if update:
                if self.update_constants:
                    to_send = self.constants
                else:
                    to_send = False
                if self.constants.threaded:
                    returns = self.threaded_update([(self.max_result, to_send),
                                                    (stage.update, stage.update_vars,
                                                     stage_type == 1)])
                else:
                    returns = self.unthreaded_update([(self.max_result, to_send),
                                                      (stage.update,
                                                       stage.update_vars, stage_type == 1)])
                if stage_type != 1:
                    self.results[stage_index] = returns[0][0]
                    stage.update_widgets(*returns[0][1])
                else:
                    stage.update_widgets(*returns[0])
            if replace:
                self.current_stages[stage_index] = [stage, image, text, remove, toggle_show]
            else:
                self.current_stages.append([stage, image, text, remove, toggle_show])

        else:
            if stage:
                stage.setup(self.stage_frame, self.constants, self.display_font)
            else:
                stage = self.defined_stages[stage_type][name](self.update_output)
                stage.setup(self.stage_frame, self.constants, self.display_font)

            self.results[stage_index] = stage.input
            if replace:
                self.current_stages[stage_index] = (stage, image, text)
            else:
                self.current_stages.append((stage, image, text))
        
        if stage_type != 1 and update:
            self.max_result = self.results[stage_index]
            self.set_output(self.max_result)
            self.switch_stage(length)
        if update:
            self.root.update()
            self.stage_scroll(None)

    def move_stages(self, range_start, range_end, amount):
        for i in range(range_start, range_end + 1):
            stage = self.current_stages[self.stage_positions[i]]

            y = 40 * (i + amount) + 36 // 2
            self.stages_last = max(self.stages_last, y + 36 // 2)
            y -= self.stages_pos

            if self.stage_positions[i] == self.selected_stage:
                self.stages_canvas.coords(stage[2], self.stages_canvas.coords(stage[1])[0], y)
            else:
                self.stages_canvas.coords(stage[2], self.stages_canvas.coords(stage[1])[0], y - 4)
            self.stages_canvas.coords(stage[1], self.stages_canvas.coords(stage[1])[0], y)
            stage[3].place(x=self.stage_up_image.width() + 25, y=y - 9)
            stage[4].place(x=3, y=y - 9)

            if amount != 0:
                self.stage_positions[i + amount] = self.stage_positions[i]
                del self.stage_positions[i]

    def remove_stage(self, stage_index, update=True):
        stage = self.current_stages[stage_index]
        pos_index = next(k for k, v in self.stage_positions.items() if v == stage_index)
        
        self.current_stages[stage_index] = None
        del self.stage_positions[pos_index]
        del self.stages_shown[stage_index]
        self.stages_canvas.delete(stage[1])
        self.stages_canvas.delete(stage[2])
        stage[3].destroy()
        stage[4].destroy()
        self.move_stages(pos_index + 1, len(self.stage_positions), -1)
        self.stages_last -= 40

        if self.selected_stage == stage_index:
            if pos_index == len(self.stage_positions):
                self.switch_stage(self.stage_positions[len(self.stage_positions) - 1], unselect=False)
            else:
                self.switch_stage(self.stage_positions[pos_index], unselect=False)
        self.remove_result(stage_index, pos_index, update=update)

        if update:
            self.root.update()
            self.stage_scroll(None)

    def remove_result(self, stage_index, pos_index, update=True):
        if stage_index in self.results:
            del self.results[stage_index]
        if pos_index != len(self.stage_positions) and update:
            self.update_output(self.current_stages[self.stage_positions[pos_index]][0])
        else:
            p_items = self.stage_positions.items()
            max_index = next(v for k, v in reversed(p_items) if v in self.results)
            self.max_result = self.results[max_index]
            self.set_output(self.max_result)

    def update_output(self, stage):
        start_stage_index = [i for i, v in enumerate(self.current_stages) if v and v[0] is stage][0]
        start_pos_index = next(k for k, v in self.stage_positions.items() if v == start_stage_index)
        p_items = self.stage_positions.items()
        updating_stages = []

        for i in range(start_pos_index, len(self.stage_positions)):
            stage_index = self.stage_positions[i]
            x = self.current_stages[stage_index][0]
            for y in self.defined_stages[0]:
                if isinstance(x, self.defined_stages[0][y]) and self.stages_shown[stage_index]:
                    updating_stages.append((stage_index, True))
                    break
            else:
                for y in self.defined_stages[1]:
                    if isinstance(x, self.defined_stages[1][y]) and self.stages_shown[stage_index]:
                        updating_stages.append((stage_index, False))
                        break
                else:
                    for y in self.defined_stages[2]:
                        if (isinstance(x, self.defined_stages[2][y])
                            and self.stages_shown[stage_index]):
                            updating_stages.append((stage_index, True))
        if start_pos_index == 0:
            self.results[0] = self.current_stages[0][0].input
        if updating_stages:
            search_item = next(k for k, v in p_items if v == updating_stages[0][0])
            to_search = list(self.stage_positions.values())
            stage = [x for x in to_search if x < search_item and x in self.results][-1]
            updating_stages.insert(0, (self.stage_positions[stage], True))

            if self.update_constants:
                updates = [(self.results[updating_stages[0][0]], self.constants)]
            else:
                updates = [(self.results[updating_stages[0][0]], False)]
            for i, v in enumerate(updating_stages[1:]):
                function = self.current_stages[v[0]][0].update
                args = self.current_stages[v[0]][0].update_vars
                if v[1]: analysis = False
                else: analysis = True
                updates.append((function, args, analysis))
            if self.constants.threaded:
                returns = self.threaded_update(updates)
            else:
                returns = self.unthreaded_update(updates)
            
            for i, v in enumerate(updating_stages[1:]):
                if v[1]:
                    self.results[v[0]] = returns[i][0]
                    self.current_stages[v[0]][0].update_widgets(*returns[i][1])
                else:
                    self.current_stages[v[0]][0].update_widgets(*returns[i])
            
        self.max_result = self.results[next(v for k, v in reversed(p_items) if v in self.results)]
        self.set_output(self.max_result)

    def unthreaded_update(self, updates):
        text, constant_args = updates.pop(0)
        if not constant_args:
            constant_args = self.constants
        returns = []
        for update in updates:
            function, args, analysis = update
            result = function(text, self.constants, *args)
            returns.append(result)
            if not analysis: text = result[0]

        return returns

    def threaded_update(self, updates):
        self.loading_animation_label.grab_set()
        self.loading = True
        self.update_constants = False
        after = self.loading_animation_label.after(250, self.start_loading_animation, 0, True)
        self.update_queue_in.put(updates)

        while True:
            if self.update_queue_out.empty():
                self.root.update()
                self.root.update_idletasks()
                time.sleep(self.constants.loading_delay / 1000)
            else:
                returns = self.update_queue_out.get()
                break

        self.loading_animation_label.grab_release()
        self.loading = False
        self.loading_animation_label.after_cancel(after)
        
        return returns

    def start_loading_animation(self, frame, start=False):
        if start == True and self.loading:
            for widget in self.stage_frame.winfo_children():
                if widget != self.loading_animation_label:
                    widget.grid_forget()
            for i in range(1, 10):
                self.stage_frame.rowconfigure(i, weight=0, minsize=0)
                self.stage_frame.columnconfigure(i, weight=0, minsize=0)
            self.stage_frame.rowconfigure(0, weight=1)
            self.stage_frame.columnconfigure(0, weight=1)
            self.loading_animation_label.grid()
            self.start_loading_animation(frame)
        elif self.loading:
            self.loading_animation_label.configure(image=self.loading_animation_images[frame])
            self.root.after(100, self.start_loading_animation, (frame + 1) % 8)
        else:
            self.loading_animation_label.grid_forget()
            self.stage_frame.rowconfigure(0, weight=0)
            self.stage_frame.columnconfigure(0, weight=0)
            self.current_stages[self.selected_stage][0].display()

if __name__ == '__main__':
    App().start()

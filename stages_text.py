from constants import *
import tkinter as tk
import customtkinter as ctk

class UpperCase(Stage):
    @staticmethod
    def update(text):
        return (text.upper(), ())
    
class LowerCase(Stage):
    @staticmethod
    def update(text):
        return (text.lower(), ())

class Reverse(Stage):
    @staticmethod
    def update(text):
        return (text[::-1], ())

class Strip(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.spaces_var = tk.IntVar()
        self.spaces_var.set(1)
        self.update_vars = (True,)
        
    def setup(self, frame):
        super().setup(frame)
        self.checkbox = ctk.CTkCheckBox(frame, text='Strip Spaces', variable=self.spaces_var,
                                        command=self.checkbox_update)

    def checkbox_update(self):
        self.update_vars = (bool(self.spaces_var.get()),)
        self.update_output(self)

    @staticmethod
    def update(text, spaces):
        if spaces:
            stripped = ''.join([c for c in text if c.lower() in alphabet])
        else:
            stripped = ''.join([c for c in text if c.lower() in alphabet + [' ']])
            
        return (stripped, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.checkbox.grid(row=0, column=0)

class Block(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.block_length_var = tk.StringVar()
        self.block_length_var.set('5')
        self.block_length_var.trace('w', self.input_update)
        self.update_vars = (5,)

    def setup(self, frame):
        super().setup(frame)
        self.label = ctk.CTkLabel(frame, text='Block Length:')
        self.input = ctk.CTkEntry(frame, textvariable=self.block_length_var, width=30)
        self.input.bind('<MouseWheel>', self.input_scroll)

    def input_update(self, var, index, mode):
        value = self.block_length_var.get()
        if value.isnumeric() and value != '0':
            self.update_vars = (int(value),)
        self.update_output(self)

    def input_scroll(self, event):
        if event.delta > 0:
            new = self.update_vars[0] + 1
        else:
            new = max(self.update_vars[0] - 1, 1)
        self.block_length_var.set(str(new))

    @staticmethod
    def update(text, block_length):
        text = text.replace(' ', '')
        blocked = ''
        if len(text) > 0:
            blocked += text[0]
            for index, character in enumerate(text[1:]):
                if (index + 1) % block_length == 0:
                    blocked += ' '
                blocked += character
        
        return (blocked, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.label.grid(row=0, column=0, sticky='E')
        self.input.grid(row=0, column=1, sticky='W')

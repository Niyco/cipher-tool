import constants
import tkinter as tk
import customtkinter as ctk

class BinaryCode(constants.Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.mode_var = tk.IntVar(value=0)
        self.letter_separator_var = tk.StringVar()
        self.word_separator_var = tk.StringVar()
        self.option_var = tk.IntVar(value=0)
        self.update_vars = (0,)
    
    def setup(self, frame, texts):
        super().setup(frame, texts)
        self.letter_separator_var.set('')
        self.word_separator_var.set('')
        self.mode_var.trace('w', self.input_update)
        self.letter_separator_var.trace('w', self.input_update)
        self.word_separator_var.trace('w', self.input_update)
        self.option_var.trace('w', self.input_update)
        self.update_vars = (self.mode_var.get(), '', '', self.option_var.get())
        self.cipher_radio_1 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=0,
                                                 text=texts['cipher_radio_1'])
        self.cipher_radio_2 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=1,
                                                 text=texts['cipher_radio_2'])
        self.cipher_radio_3 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=2,
                                                 text=texts['cipher_radio_3'])
        self.cipher_radio_4 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=3,
                                                 text=texts['cipher_radio_4'])
        self.option_radio_1 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=texts['option_radio_1'])
        self.option_radio_2 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=texts['option_radio_2'])
        self.option_radio_3 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=texts['option_radio_3'])
        self.option_radio_4 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=texts['option_radio_4'])
        self.option_radio_5 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=texts['option_radio_5'])
        self.option_radio_6 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=texts['option_radio_6'])
        self.label_1 = ctk.CTkLabel(frame, text=texts['label_1'])
        self.input_1 = ctk.CTkEntry(frame, textvariable=self.letter_separator_var, width=60)
        self.label_2 = ctk.CTkLabel(frame, text=texts['label_2'])
        self.input_2 = ctk.CTkEntry(frame, textvariable=self.word_separator_var, width=60)
    
    def input_update(self, var_name, index, mode):
        if var_name == str(self.mode_var):
            self.display()
            value = self.mode_var.get()
            self.update_vars = (value, self.update_vars[1], self.update_vars[2], self.update_vars[3])
        elif var_name == str(self.letter_separator_var):
            var = self.letter_separator_var
            value = var.get()
            if value == self.texts['space']:
                value = ' '
            elif value == ' ':
                var.set(self.texts['space'])
            self.update_vars = (self.update_vars[0], value, self.update_vars[2], self.update_vars[3])
        elif var_name == str(self.word_separator_var):
            var = self.word_separator_var
            value = var.get()
            if value == self.texts['space']:
                value = ' '
            elif value == ' ':
                var.set(self.texts['space'])
            self.update_vars = (self.update_vars[0], self.update_vars[1], value, self.update_vars[3])
        elif var_name == str(self.option_var):
            value = self.option_var.get()
            self.update_vars = (self.update_vars[0], self.update_vars[1], self.update_vars[2], value)
            
        self.update_output(self)
        
    @staticmethod
    def update(text, mode, letter_separator, word_separator, option):
        if len(text) == 0:
            return (text, ())
        if mode == 0:
            codes = constants.morse_codes
        elif mode == 1:
            codes = constants.baconian_codes
            if option == 1:
                new_codes = {}
                to_add = 0
                for index, item in enumerate(codes.items()):
                    k, v = item
                    if index == 9 or index == 21:
                        to_add += 1
                    k = k.replace('a', '0').replace('b', '1')
                    k = format(int(k, 2) + to_add, '05b')
                    k = k.replace('0', 'a').replace('1', 'b')
                    new_codes[k] = v
                codes = new_codes
        elif mode == 2:
            codes = constants.binary_codes
            if option == 1:
                codes = {format(int(k, 2) + 1, '05b'): v for k, v in codes.items()}
        if mode == 3:
            codes = constants.baudot_codes
            if option == 1:
                codes = {k[::-1]: v for k, v in codes.items()}
                
            result = ''
            def decode_word(word, shift):
                decoded_word = ''
                for char in word.split(letter_separator):
                    if char in codes:
                        new_char = codes[char][shift]
                        if new_char == 'LS':
                            shift = 0
                        elif new_char == 'FS':
                            shift = 1
                        else:
                            decoded_word += new_char
                return decoded_word, shift
        else:
            def decode_word(word, shift):
                decoded_word = ''
                for char in word.split(letter_separator):
                    if char in codes:
                        decoded_word += codes[char]
                return decoded_word, shift

        result = ''
        if word_separator != '' and letter_separator != '':
            shift = 0
            for word in text.split(word_separator):
                decoded_word, shift = decode_word(word, shift)
                result += ' '
            result = result[:-1]
        elif letter_separator != '':
            result, shift = decode_word(text, 0)
        elif mode:
            text.replace(' ', '')
            blocked = ['']
            for index, character in enumerate(text):
                blocked[-1] += character
                if (index + 1) % 5 == 0:
                    blocked.append('')
            letter_separator = ' '
            shift = 0
            for char in blocked:
                decoded_char, shift = decode_word(char, shift)
        if not result:
            result = text
        
        return (result, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1, minsize=325)
        self.frame.columnconfigure(3, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(4, minsize=65)
        self.frame.rowconfigure(5, minsize=65)
        self.frame.rowconfigure(6, weight=1)
        self.cipher_radio_1.grid(column=0, row=0, padx=30, pady=6, sticky='WS')
        self.cipher_radio_2.grid(column=0, row=1, padx=30, pady=6, sticky='W')
        self.cipher_radio_3.grid(column=0, row=2, padx=30, pady=6, sticky='W')
        self.cipher_radio_4.grid(column=0, row=3, padx=30, pady=6, sticky='W')
        self.label_1.grid(column=1, row=1, sticky='E')
        self.input_1.grid(column=2, row=1, sticky='W')
        self.label_2.grid(column=1, row=2, sticky='E')
        self.input_2.grid(column=2, row=2, sticky='W')

        options_radios = [self.option_radio_1, self.option_radio_2, self.option_radio_3,
                          self.option_radio_4, self.option_radio_5, self.option_radio_6]
        mode = self.mode_var.get()
        grid_add = options_radios[(mode - 1) * 2:mode * 2]
        grid_forget = set(options_radios[:(mode - 1) * 2] + options_radios[(mode) * 2:])

        for widget in grid_forget:
            widget.grid_forget()
        if grid_add:
            grid_add[0].grid(column=0, row=4, padx=30, pady=15, sticky='WS')
            grid_add[1].grid(column=0, row=5, padx=30, pady=0, sticky='NW')
            

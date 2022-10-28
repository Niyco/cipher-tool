from defined import Stage
import tkinter as tk
import customtkinter as ctk

class Length(Stage):
    def setup(self, frame, constants):
        super().setup(self, frame, constants)
        self.length_var = tk.StringVar()
        self.length_var.set('0')
        self.length_widget = ctk.CTkLabel(self.frame, textvariable=self.length_var)

    @staticmethod
    def update(text, constants):
        length = len(text)

        return (length,)

    def update_widgets(self, length):
        self.length_var.set(self.texts['label'] + ' ' + str(length))
    
    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.length_widget.grid(row=0, column=0)

class Frequency(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.mode_var = tk.IntVar()
        self.mode_var.set(0)
        self.mode_var.trace('w', self.input_update)
        self.alpha_ex_var = tk.IntVar()
        self.alpha_ex_var.set(1)
        self.alpha_ex_var.trace('w', self.input_update)
        self.update_vars.extend([0, 1])
    
    def setup(self, frame, constants):
        super().setup(self, frame, constants)
        self.radio_1 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=0, text=self.texts['radio_1'])
        self.radio_2 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=1, text=self.texts['radio_2'])
        self.radio_3 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=2, text=self.texts['radio_3'])
        self.checkbox = ctk.CTkCheckBox(frame, variable=self.alpha_ex_var, text=self.texts['checkbox'])
        self.textbox = tk.Text(frame, bd=0, bg=self.constants.theme['color']['entry'][self.constants.mode],
                               fg=constants.theme['color']['text'][self.constants.mode], width=40,
                               insertbackground=self.constants.theme['color']['text'][self.constants.mode])
        self.scrollbar = ctk.CTkScrollbar(frame, command=self.textbox.yview)
        self.textbox.configure(yscrollcommand=self.scrollbar.set)

    def input_update(self, var, index, mode):
        if var == str(self.mode_var):
            value = self.mode_var.get()
            self.update_vars[0] = value
        else:
            value = self.alpha_ex_var.get()
            self.update_vars[1] = value
        self.update_output(self)
        
    @staticmethod
    def update(text, constants, mode, alpha_ex):
        text = text.lower().replace('\n', '')
        frequencies = {}
        text_length = len(text)
        for i in range(text_length - mode):
            chars = text[i:i + mode + 1]
            if alpha_ex and False in {char in constants.alphabet for char in chars}:
                continue
            if chars in frequencies:
                frequencies[chars] += 1
            else:
                frequencies[chars] = 1
        for k in frequencies.keys():
            frequencies[k] /= text_length
        frequencies = dict(sorted(frequencies.items(), key=lambda e: e[1], reverse=True))
        
        return (frequencies,)

    def update_widgets(self, frequencies):
        formatted = ''
        for k in frequencies:
            v = frequencies[k]
            formatted += f'\'{k}\': {round(v * 100, 2)}%\n'
            
        self.textbox.delete(1.0, 'end')
        self.textbox.insert(1.0, formatted)

    def display(self):
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.radio_1.grid(column=0, row=0, padx=30, pady=6, sticky='SW')
        self.radio_2.grid(column=0, row=1, padx=30, pady=6, sticky='W')
        self.radio_3.grid(column=0, row=2, padx=30, pady=6, sticky='W')
        self.checkbox.grid(column=0, row=3, padx=25, pady=15, sticky='NW')
        self.textbox.grid(column=1, row=0, pady=80, rowspan=4, sticky='NS')
        self.scrollbar.grid(column=2, row=0, rowspan=4, sticky='NSW')

class IoC(Stage):
    def setup(self, frame, constants):
        super().setup(self, frame, constants)
        self.ioc_var = tk.StringVar()
        self.label = ctk.CTkLabel(self.frame, textvariable=self.ioc_var)

    @staticmethod
    def update(text, constants):
        if len(text) > 1:
            length = len([c for c in text if c.lower() in constants.alphabet])
            length = length * (length - 1)
            letter_freqs = [text.lower().count(letter) for letter in constants.alphabet]
            ioc = sum([letter_freq * (letter_freq - 1) / length for letter_freq in letter_freqs])
        else:
            ioc = 0

        return (ioc,)

    def update_widgets(self, ioc):
        accuracy = 5
        language_difference = round(self.constants.language_ioc - ioc, accuracy)
        language_difference_str = ' ('
        if language_difference >= 0:
            language_difference_str += '+'
        language_difference_str += str(language_difference) + ')'
        random_difference = round(1 / 26 - ioc, accuracy)
        random_difference_str = ' ('
        if random_difference >= 0:
            random_difference_str += '+'
        random_difference_str += str(random_difference) + ')'
        
        formatted = (self.texts['text_ioc'] + ' ' + str(round(ioc, accuracy)) + '\n\n' + self.texts['english_ioc']
                     + ' '+ str(round(self.constants.language_ioc, accuracy)) + language_difference_str + '\n'
                     + self.texts['random_ioc'] + ' ' + str(round(1 / 26, accuracy)) + random_difference_str)
        self.ioc_var.set(formatted)
    
    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.label.grid(row=0, column=0)

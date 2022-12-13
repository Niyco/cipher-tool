from defined import Stage, CustomSlider, DisplayText, InsertEntry
import tkinter as tk
import customtkinter as ctk
import unicodedata
import pickle
import base64

class BinaryCode(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode_var = tk.IntVar(value=0)
        self.mode_var = tk.IntVar(value=0)
        self.option_var = tk.IntVar(value=0)
        self.letter_separator_var = tk.StringVar(value='')
        self.word_separator_var = tk.StringVar(value='')
        self.update_vars.extend([0, 0, 0])
    
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.mode_var.trace('w', self.input_update)
        self.encode_var.trace('w', self.input_update)
        self.letter_separator_var.trace('w', self.input_update)
        self.word_separator_var.trace('w', self.input_update)
        self.option_var.trace('w', self.input_update)
        self.update_vars.extend([self.letter_separator_var.get(), self.word_separator_var.get()])
        self.encode = ctk.CTkSwitch(frame, text=self.texts['encode'], onvalue=1, offvalue=0,
                                    variable=self.encode_var, font=self.font)
        self.cipher_radio_1 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=0,
                                                 text=self.texts['cipher_radio_1'], font=self.font)
        self.cipher_radio_2 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=1,
                                                 text=self.texts['cipher_radio_2'], font=self.font)
        self.cipher_radio_3 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=2,
                                                 text=self.texts['cipher_radio_3'], font=self.font)
        self.cipher_radio_4 = ctk.CTkRadioButton(frame, variable=self.mode_var, value=3,
                                                 text=self.texts['cipher_radio_4'], font=self.font)
        self.option_radio_1 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=self.texts['option_radio_1'], font=self.font)
        self.option_radio_2 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=self.texts['option_radio_2'], font=self.font)
        self.option_radio_3 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=self.texts['option_radio_3'], font=self.font)
        self.option_radio_4 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=self.texts['option_radio_4'], font=self.font)
        self.option_radio_5 = ctk.CTkRadioButton(frame, variable=self.option_var, value=0,
                                                 text=self.texts['option_radio_5'], font=self.font)
        self.option_radio_6 = ctk.CTkRadioButton(frame, variable=self.option_var, value=1,
                                                 text=self.texts['option_radio_6'], font=self.font)
        self.label_1 = ctk.CTkLabel(frame, text=self.texts['label_1'], font=self.font)
        self.input_1 = ctk.CTkEntry(frame, textvariable=self.letter_separator_var, width=60,
                                    font=self.font)
        self.label_2 = ctk.CTkLabel(frame, text=self.texts['label_2'], font=self.font)
        self.input_2 = ctk.CTkEntry(frame, textvariable=self.word_separator_var, width=60,
                                    font=self.font)
    
    def input_update(self, var_name, index, mode):
        if var_name == str(self.encode_var):
            value = self.encode_var.get()
            if value:
                self.label_1.grid_forget()
                self.input_1.grid_forget()
                self.label_2.grid_forget()
                self.input_2.grid_forget()
            else:
                self.label_1.grid(column=0, row=1, columnspan=2, sticky='E', padx=8)
                self.input_1.grid(column=2, row=1, sticky='W')
                self.label_2.grid(column=0, row=2, columnspan=2, sticky='E', padx=8)
                self.input_2.grid(column=2, row=2, sticky='W')

            index = 0
        elif var_name == str(self.mode_var):
            self.display()
            value = self.mode_var.get()
            index = 1
        elif var_name == str(self.option_var):
            value = self.option_var.get()
            index = 2
        elif var_name == str(self.letter_separator_var):
            var = self.letter_separator_var
            value = var.get()
            if value == self.texts['space']:
                value = ' '
            elif value == ' ':
                var.set(self.texts['space'])
            index = 3
        elif var_name == str(self.word_separator_var):
            var = self.word_separator_var
            value = var.get()
            if value == self.texts['space']:
                value = ' '
            elif value == ' ':
                var.set(self.texts['space'])
            index = 4

        self.update_vars[index] = value
        self.update_output(self)
        
    @staticmethod
    def update(text, constants, encode, mode, option, letter_separator, word_separator):
        if len(text) == 0:
            return (text, ())
        text_original = text
        text = text.lower()
        
        if mode == 0:
            codes = constants.morse_codes
            if encode:
                codes = {v: k for k, v in codes.items()}
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
                    if encode:
                        new_codes[v] = k
                    else:
                        new_codes[k] = v
                codes = new_codes
            elif encode:
                codes = {v: k for k, v in codes.items()}
        elif mode == 2:
            codes = constants.binary_codes
            if option == 1:
                codes = {format(int(k, 2) + 1, '05b'): v for k, v in codes.items()}
            if encode:
                codes = {v: k for k, v in codes.items()}
        if mode == 3:
            codes = constants.baudot_codes
            if option == 1:
                codes = {k[::-1]: v for k, v in codes.items()}
            if encode:
                new_codes_1 = {}
                new_codes_2 = {}
                for k, v in codes.items():
                    new_codes_1[v[0]] = k
                    new_codes_2[v[1]] = k
                codes = (new_codes_1, new_codes_2)

                def encode_letter(letter, shift):
                    for i in range(len(codes)):
                        if letter in codes[i]:
                            new_letter = codes[i][letter]
                            if shift != i and (i != 1 or letter not in codes[0]):
                                if i:
                                    new_letter = codes[i]['FS'] + letter_separator + new_letter
                                else:
                                    new_letter = codes[i]['LS'] + letter_separator + new_letter
                                shift = i
                            return new_letter, shift
                    return '', shift
                        
                        
            else:
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
        elif encode:
            def encode_letter(letter, shift):
                if letter in codes:
                    return codes[letter], shift
                return '', shift
        else:
            def decode_word(word, shift):
                decoded_word = ''
                for char in word.split(letter_separator):
                    if char in codes:
                        decoded_word += codes[char]
                return decoded_word, shift
        result = ''
            
        if encode:
            shift = 0

            if mode == 3:
                for letter in text:
                    encoded_letter, shift = encode_letter(letter, shift)
                    result += encoded_letter
                
            else:
                words = text.split(' ')
                
                for word in words:
                    if word:
                        for letter in word:
                            encoded_letter, shift = encode_letter(letter, shift)
                            result += encoded_letter
                            if letter_separator != '' and encoded_letter:
                                result += letter_separator
                        if word_separator != '':
                            result += word_separator + letter_separator
                if word_separator != '':
                    result = result.removesuffix(word_separator + letter_separator)
                result = result.removesuffix(letter_separator)

        else:
            if word_separator != '' and letter_separator != '':
                shift = 0
                for word in text.split(word_separator):
                    decoded_word, shift = decode_word(word, shift)
                    result += decoded_word
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
                    result += decoded_char
                    
            if not result.replace(' ', ''):
                result = text_original
        
        return (result, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1, minsize=250)
        self.frame.columnconfigure(3, weight=0)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(4, minsize=65)
        self.frame.rowconfigure(5, minsize=65)
        self.frame.rowconfigure(6, weight=1)
        self.cipher_radio_1.grid(column=0, row=0, padx=30, pady=6, sticky='WS')
        self.cipher_radio_2.grid(column=0, row=1, padx=30, pady=6, sticky='W')
        self.cipher_radio_3.grid(column=0, row=2, padx=30, pady=6, sticky='W')
        self.cipher_radio_4.grid(column=0, row=3, padx=30, pady=6, sticky='W')
        self.encode.grid(column=2, row=6, padx=15, pady=15, sticky='SE')

        encode = self.encode_var.get()
        if not encode:
            self.label_1.grid(column=0, row=1, columnspan=2, sticky='E', padx=8)
            self.input_1.grid(column=2, row=1, sticky='W')
            self.label_2.grid(column=0, row=2, columnspan=2, sticky='E', padx=8)
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

class Caesar(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode_var = tk.IntVar(value=0)
        self.shift_var = tk.IntVar(value=0)
        self.update_vars.extend([0, 0])

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.encode_switch = ctk.CTkSwitch(frame, text=self.texts['encode'], onvalue=1, offvalue=0,
                                    variable=self.encode_var, font=self.font)
        self.shift_slider = CustomSlider(frame, from_=0, to=25, number_of_steps=25, width=375,
                                         variable=self.shift_var, slider_cb=self.update_label,
                                         var_cb=self.update_shift, loop=True)
        self.label = ctk.CTkLabel(frame, text=self.texts['label'] + ' ' + str(self.shift_var.get()),
                                  font=self.font)
        self.text = ctk.CTkEntry(frame, font=self.font)
        self.encode_var.trace('w', self.trace_update)

    def update_label(self, variable, value): 
        self.label.configure(text=self.texts['label'] + ' ' + str(value))

    def update_shift(self, variable, value):
        self.update_vars[1] = value
        self.update_output(self)

    def trace_update(self, var_name, index, mode):
        self.update_output(self)

    @staticmethod
    def update(text, constants, encode, shift):
        if encode:
            shift = 26 - shift
            
        shifted = ''
        for letter in text:
            if letter.lower() in constants.alphabet:
                index = (constants.alphabet.index(letter.lower()) - shift) % 26
                shifted_letter = constants.alphabet[index]

                if encode:
                    shifted_letter = shifted_letter.upper()
                shifted += shifted_letter
            else:
                shifted += letter
        
        return (shifted, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.encode_switch.grid(row=1, column=0, padx=15, pady=15, sticky='SE')
        self.label.grid(row=0, column=0, pady=20, sticky='S')
        self.shift_slider.grid(row=1, column=0, sticky='N')

class Substitution(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode_var = tk.IntVar(value=0)
        self.substitutions = {}
        self.update_vars.extend([0, {}])
        
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        bg_color = self.constants.theme['CTkEntry']['fg_color'][self.constants.mode]
        self.encode_switch = ctk.CTkSwitch(frame, text=self.texts['encode'], onvalue=1, offvalue=0,
                                           variable=self.encode_var, font=self.font)
        self.input_1 = ctk.CTkEntry(frame, width=60, font=self.font)
        self.label = ctk.CTkLabel(frame, text='->', width=20, font=self.font)
        self.input_2 = ctk.CTkEntry(frame, width=60, font=self.font)
        self.button_1 = ctk.CTkButton(frame, text=self.texts['button_1'], width=110, font=self.font,
                                      command=self.substitute)
        self.button_2 = ctk.CTkButton(frame, text=self.texts['button_2'], width=110, font=self.font,
                                      command=self.unsubstitute)
        self.textbox = DisplayText(frame, width=110, height=435, font=self.font, fg_color=bg_color)
        self.keyword = ctk.CTkButton(frame, text=self.texts['keyword'], command=self.get_keyword,
                                     font=self.font)

        self.input_1.bind('<Tab>', lambda event: self.tab_order(0))
        self.input_2.bind('<Tab>', lambda event: self.tab_order(1))
        self.button_1.bind('<Tab>', lambda event: self.tab_order(2))
        self.button_2.bind('<Tab>', lambda event: self.tab_order(3))
        self.button_1.bind('<space>', self.substitute)
        self.button_2.bind('<space>', self.unsubstitute)
        self.textbox.bind('<Control-c>', self.copy)
        self.textbox.bind('<Control-v>', self.paste)
        self.encode_var.trace('w', self.encode_switch_update)
        self.update_substitutions()

    def encode_switch_update(self, var, index, mode):
        self.update_vars[0] = self.encode_var.get()
        self.update_substitutions()
        self.input_1.configure(state='normal')
        self.update_output(self)

    def get_keyword(self):
        dialog = ctk.CTkInputDialog(text=self.texts['keyword'] + ':', title=self.texts['keyword'])
        keyword = dialog.get_input()
        keyword = {x.lower(): None for x in keyword if x.lower() in self.constants.alphabet}
        keyword = ''.join(list(keyword))
        self.substitutions = {}
        
        key_index = 0
        value_index = 0
        while key_index < len(keyword):
            self.substitutions[self.constants.alphabet[key_index].upper()] = keyword[value_index]

            key_index += 1
            value_index += 1

        value_index = 0
        while key_index < len(self.constants.alphabet):
            if self.constants.alphabet[value_index] in self.substitutions.values():
                value_index += 1
                continue
            else:
                v = self.constants.alphabet[value_index]
                self.substitutions[self.constants.alphabet[key_index].upper()] = v

            key_index += 1
            value_index += 1
                    
        self.update_vars[1] = self.substitutions
        self.update_substitutions()
        self.update_output(self)
    
    def tab_order(self, index):
        if index == 0:
            if self.encode_var.get():
                self.button_1.focus()
                hover_color = self.constants.theme['color']['button_hover'][self.constants.mode]
                self.button_1.configure(fg_color=hover_color)
            else:
                self.input_2.focus()
                return
            
        elif index == 1:
            if self.encode_var.get():
                self.input_1.configure(state='normal')
                self.input_1.focus()
                return
            else:
                self.button_1.focus()
                hover_color = self.constants.theme['color']['button_hover'][self.constants.mode]
                self.button_1.configure(fg_color=hover_color)
        
        elif index == 2:
            self.button_2.focus()
            default_color = self.constants.theme['color']['button'][self.constants.mode]
            hover_color = self.constants.theme['color']['button_hover'][self.constants.mode]
            self.button_1.configure(fg_color=default_color)
            self.button_2.configure(fg_color=hover_color)
        
        elif index == 3:
            default_color = self.constants.theme['color']['button'][self.constants.mode]
            if self.encode_var.get():
                self.input_1.configure(state='disabled')
                self.input_2.focus()
                self.button_2.configure(fg_color=default_color)
                return
            else:
                self.input_1.focus()
                self.button_2.configure(fg_color=default_color)
                return

        return 'break'

    def substitute(self, *args):
        input_1 = self.input_1.get()
        input_2 = self.input_2.get()
            
        if input_1 != input_2:
            if len(input_1) == len(input_2):
                for i, c in enumerate(input_1):
                    self.substitutions[c] = input_2[i]
            elif input_2 == '':
                for i, c in enumerate(input_1):
                    self.substitutions[c] = ''
                
        self.update_vars[1] = self.substitutions
        self.update_substitutions()
        self.update_output(self)

    def unsubstitute(self, *args):
        input_1 = self.input_1.get()
        input_2 = self.input_2.get()
            
        if input_1 != input_2:
            if len(input_1) == len(input_2):
                for i, c in enumerate(input_1):
                    if c in self.substitutions and input_2[i] in self.substitutions.values():
                        del self.substitutions[c]
            elif input_2 == '':
                for i, c in enumerate(input_1):
                    if c in self.substitutions:
                        del self.substitutions[c]
                    
        self.update_vars[1] = self.substitutions
        self.update_substitutions()
        self.update_output(self)

    def copy(self, event):
        value = base64.b64encode(pickle.dumps(self.substitutions))
        self.frame.master.clipboard_clear()
        self.frame.master.clipboard_append(value.decode('utf-8'))
        self.frame.master.update()
        
    def paste(self, event):
        try:
            self.substitutions = pickle.loads(base64.b64decode(self.frame.master.clipboard_get()))
            self.update_vars[1] = self.substitutions
            self.update_substitutions()
            self.update_output(self)
        except pickle.UnpicklingError:
            pass
    
    @staticmethod
    def update(text, constants, encode, substitutions):
        if encode:
            substitutions = {v: k for k, v in substitutions.items()}

        result = ''
        for c in text:
            if c in substitutions:
                result += substitutions[c]
            else:
                result += c
        
        return (result, ())

    def update_substitutions(self):
        substitutions = self.substitutions.copy()

        if self.encode_var.get():
            arrow = '<-'
        else:
            arrow = '->'
            
        for letter in self.constants.alphabet:
            if letter.upper() not in substitutions:
                substitutions[letter.upper()] = ''
        substitutions = dict(sorted(substitutions.items(), key=self.substitutions_sort_key))

        formatted = '\n'.join([f'\'{k}\' {arrow} \'{v}\'' for k, v in substitutions.items()])

        self.textbox.configure(state='normal')
        self.textbox.delete(1.0, 'end')
        self.textbox.insert(1.0, formatted)
        self.textbox.configure(state='disabled')
        self.label.configure(text=arrow)

    def substitutions_sort_key(self, element):
        key = element[0]
        if key.lower() in self.constants.alphabet:
            return self.constants.alphabet.index(key.lower())
        else:
            return -1

    def display(self):
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, minsize=15)
        self.frame.columnconfigure(4, minsize=120)
        self.frame.columnconfigure(5, weight=1)
        
        self.input_1.grid(row=0, column=1, rowspan=2, padx=15)
        self.label.grid(row=0, column=2, rowspan=2)
        self.input_2.grid(row=0, column=3, rowspan=2, padx=10)
        self.button_1.grid(row=0, column=4, pady=12, sticky='S')
        self.button_2.grid(row=1, column=4, pady=12, sticky='N')
        self.keyword.grid(row=1, column=1, columnspan=3)
        self.textbox.grid(row=0, column=5, rowspan=2, columnspan=2)
        self.encode_switch.grid(row=1, column=6, padx=15, pady=15, sticky='SE')
        
        button_color = self.constants.theme['CTkButton']['fg_color'][self.constants.mode]
        self.button_1.configure(fg_color=button_color)
        self.button_2.configure(fg_color=button_color)

class Affine(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode_var = tk.IntVar(value=0)
        self.alpha_var = tk.IntVar(value=0)
        self.beta_var = tk.IntVar(value=0)
        self.update_vars.extend([0, 0, 0])

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.update_vars[1] = list(self.constants.inverses.keys())[self.alpha_var.get()]

        self.encode_switch = ctk.CTkSwitch(frame, text=self.texts['encode'], onvalue=1, offvalue=0,
                                           variable=self.encode_var, font=self.font)
        self.alpha_label = ctk.CTkLabel(frame, text=(self.texts['alpha_label']
                                             + ' ' + str(self.update_vars[1])), font=self.font)
        self.beta_label = ctk.CTkLabel(frame, text=(self.texts['beta_label']
                                                    + ' ' + str(self.update_vars[2])),
                                       font=self.font)
        self.alpha_slider = CustomSlider(frame, from_=0, to=11, number_of_steps=11, width=375,
                                         variable=self.alpha_var, slider_cb=self.label_update,
                                         var_cb=lambda *args: self.update_output(self))
        self.beta_slider = CustomSlider(frame, from_=0, to=25, number_of_steps=25, width=375,
                                        variable=self.beta_var, slider_cb=self.label_update,
                                        var_cb=lambda *args: self.update_output(self), loop=True)
        self.encode_var.trace('w', self.encode_update)
   
    def label_update(self, variable, value):
        if variable == self.alpha_var:
            self.update_vars[1] = list(self.constants.inverses.keys())[self.alpha_var.get()]
            self.alpha_label.configure(text=(self.texts['alpha_label']
                                             + ' ' + str(self.update_vars[1])))
        else:
            if self.beta_var.get() == 0 and self.update_vars[2] == 25:
                self.alpha_var.set((self.alpha_var.get() + 1) % 12)
            elif self.beta_var.get() == 25 and self.update_vars[2] == 0:
                self.alpha_var.set((self.alpha_var.get() - 1) % 12)
            self.update_vars[2] = self.beta_var.get()
            self.beta_label.configure(text=self.texts['beta_label'] + ' ' + str(self.update_vars[2]))

    def encode_update(self, *args):
        self.update_vars[0] = self.encode_var.get()
        self.update_output(self)

    @staticmethod
    def update(text, constants, encode, alpha, beta):
        shifted = ''
        for letter in text:
            if letter.lower() in constants.alphabet:
                if encode:
                    index = (constants.alphabet.index(letter.lower()) * alpha + beta) % 26
                else:
                    index = ((constants.alphabet.index(letter.lower()) - beta)
                             * constants.inverses[alpha]) % 26
                shifted_letter = constants.alphabet[index]
                if encode:
                    shifted_letter = shifted_letter.upper()
                shifted += shifted_letter
            else:
                shifted += letter
        
        return (shifted, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.alpha_label.grid(row=0, column=0, sticky='S')
        self.alpha_slider.grid(row=1, column=0, pady=10)
        self.beta_label.grid(row=2, column=0, pady=10)
        self.beta_slider.grid(row=3, column=0, sticky='N')
        self.encode_switch.grid(row=4, column=0, padx=15, pady=15, sticky='SE')

class Vigenere(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode = tk.IntVar(value=0)
        self.mode = tk.IntVar(value=0)
        self.keyword_length = tk.StringVar(value='5')
        self.raw_kw = tk.StringVar()
        self.encode.trace('w', self.update_mode)
        self.mode.trace('w', self.update_mode)
        self.keyword_length.trace('w', self.update_key_length)
        self.raw_kw.trace('w', self.raw_kw_update)
        self.update_vars.extend([0, 0, 5, 'AAAAA'])

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.kw_len_label = ctk.CTkLabel(frame, text=self.texts['keyword_length'], font=self.font)
        self.kw_label = ctk.CTkLabel(frame, text=self.texts['keyword_contents'], font=self.font)
        self.kw_len_input = ctk.CTkEntry(frame, textvariable=self.keyword_length, width=30,
                                         justify='center', takefocus=0, font=self.font)
        self.kw_input = InsertEntry(frame, width=55, font=self.font, cb=self.update_keyword,
                                    alphabet=self.constants.alphabet)
        self.raw_kw_input = ctk.CTkEntry(frame, textvariable=self.raw_kw, justify='center',
                                         font=self.font)
        self.radio_vigenere = ctk.CTkRadioButton(frame, variable=self.mode, value=0,
                                                 text=self.texts['radio_vigenere'], font=self.font)
        self.radio_beaufort = ctk.CTkRadioButton(frame, variable=self.mode, value=1,
                                               text=self.texts['radio_beaufort'], font=self.font)
        self.encode_switch = ctk.CTkSwitch(frame, variable=self.encode, text=self.texts['encode'],
                                           font=self.font)
        self.kw_input.insert(0, self.update_vars[3])
        self.kw_len_input.bind('<MouseWheel>', self.scroll_length)
        self.kw_label.bind('<Left>', self.cycle_left)
        self.kw_label.bind('<Right>', self.cycle_right)
        self.kw_label.bind('<Tab>', self.tab_keybind)
        self.kw_len_input.bind('<Tab>', self.tab_keybind)
        self.kw_input.bind('<Tab>', self.tab_keybind)
        self.frequencies = []
        self.tabs = []
        self.updated = None
        frame_color = self.constants.theme['CTkEntry']['fg_color'][self.constants.mode]
        self.tabview = ctk.CTkTabview(self.frame, fg_color=frame_color, border_width=2,
                                      command=self.tab_select)
        for i in range(self.update_vars[2]):
            self.add_tab()

    def raw_kw_update(self, *args):
        value = self.raw_kw.get()
        length = len(value)
        if False not in [c.lower() in self.constants.alphabet for c in value] and length > 0:
            self.update_vars[3] = value
            self.update_vars[2] = length
            self.update_output(self)

    def cycle_left(self, event):
        index = int(self.tabview.get())
        current_letter = self.tabs[index][0].lower()
        char = self.constants.alphabet[(self.constants.alphabet.index(current_letter) - 1) % 26]
        new_keyword = list(self.update_vars[3])
        new_keyword[index] = char.upper()

        self.update_keyword(''.join(new_keyword))

    def cycle_right(self, event): 
        index = int(self.tabview.get())
        current_letter = self.tabs[index][0].lower()
        char = self.constants.alphabet[(self.constants.alphabet.index(current_letter) + 1) % 26]
        new_keyword = list(self.update_vars[3])
        new_keyword[index] = char.upper()

        self.update_keyword(''.join(new_keyword))

    def tab_keybind(self, event):
        self.tabview.set(str((int(self.tabview.get()) + 1) % len(self.tabs)))
        self.update_graph(None)
        return 'break'

    def scroll_length(self, event):
        if event.delta > 0:
            self.keyword_length.set(str(min(int(self.keyword_length.get()) + 1, 14)))
        else:
            if self.keyword_length.get() == '1':
                self.kw_input.delete(0, 1)
                self.kw_input.insert(0, 'A')
                if len(self.tabs) != 1:
                    self.update_key_length()
                self.update_keyword('A')
            else:
                self.keyword_length.set(str(max(int(self.keyword_length.get()) - 1, 1)))

    def update_mode(self, var, index, mode):
        if var == str(self.encode):
            self.update_vars[0] = self.encode.get()
            for widget in self.frame.winfo_children():
                widget.grid_forget()
            for i in range(0, 10):
                self.frame.rowconfigure(i, weight=0, minsize=0)
                self.frame.columnconfigure(i, weight=0, minsize=0)
            self.display()

        else:
            self.update_vars[1] = self.mode.get()
                                                        
        self.update_output(self)

    def update_key_length(self, *args):
        length = self.keyword_length.get()
        if length.isnumeric():
            length = int(length)
            if 0 < length and length < 15:
                previous = self.update_vars[2]
                difference = abs(length - previous)

                if length > previous:
                    for i in range(difference):
                        self.add_tab()
                    self.update_vars[2] = length
                    self.kw_input.configure(width=13 + 8 * length)
                    self.kw_input.insert('end', 'A' * difference)
                    self.update_vars[3] = self.update_vars[3] + 'A' * difference
                    self.update_output(self)

                elif length < previous:
                    for i in range(difference):
                        index = len(self.tabs) - 1
                        self.tabview.delete(str(index))
                        self.tabs.pop(index)
                    self.update_vars[2] = length
                    self.kw_input.configure(width=13 + 8 * length)
                    self.kw_input.delete(length, 'end')
                    self.update_vars[3] = self.update_vars[3][:0 - difference]
                    self.update_output(self)

    def update_keyword(self, keyword, update=True):
        tabs_keyword = ''.join([e[0] for e in self.tabs])
        if keyword != tabs_keyword:
            index, char = next((str(i), v) for i, v in enumerate(keyword) if v != tabs_keyword[i])

            self.tabview._segmented_button._buttons_dict[index].configure(text=char) 
            self.tabs[int(index)][0] = char
            self.tabs[int(index)][3].set(self.constants.alphabet.index(char.lower()),
                                         from_variable_callback=True)
            self.update_vars[3] = keyword
            self.tabview.set(index)
            self.update_graph(None)
            if update:
                self.update_output(self)

    def add_tab(self):
        index = len(self.tabs)
        tab = self.tabview.insert(index, str(index))
        self.tabview._segmented_button._buttons_dict[str(index)].configure(text='A') 
        self.frequencies.append([0] * 26)
    
        bg = self.constants.theme['CTkEntry']['fg_color'][self.constants.mode]
        label = ctk.CTkLabel(tab, text=self.texts['frequencies'])
        canvas = tk.Canvas(tab, highlightthickness=0, bg=bg)
        canvas.bind('<Configure>', self.update_graph)
        slider = CustomSlider(tab, from_=0, to=25, number_of_steps=25,
                              variable=tk.IntVar(), slider_cb=self.slider_update, loop=True)
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)
        label.grid(row=0, column=0)
        canvas.grid(row=1, column=0, pady=10, sticky='NSEW')
        slider.grid(row=2, column=0, padx=2, sticky='EW')
        self.tabs.insert(index, ['A', tab, canvas, slider])

    def slider_update(self, variable, value):
        index = int(self.tabview.get())
        self.kw_input.delete(index, index + 1)
        self.kw_input.insert(index, self.constants.alphabet[value].upper())
        self.update_keyword(self.kw_input.get(), update=False)
        
    def update_graph(self, event):
        if event:
            canvas = event.widget
            height = event.height
            width = event.width
        else:
            canvas = self.tabs[int(self.tabview.get())][2]
            height = canvas.winfo_height()
            width = canvas.winfo_width()
        
        index = int(self.tabview.get())
        shift = self.constants.alphabet.index(self.tabs[index][0].lower())
        encrypted_frequencies = self.frequencies[index]
        encrypted_frequencies = encrypted_frequencies[shift:] + encrypted_frequencies[:shift]
        plaintext_multi = height / list(self.constants.letter_frequencies.values())[0] // 2.1
        if max(encrypted_frequencies) > 0:
            encrypted_multi = min(height / max(encrypted_frequencies) // 2.1, plaintext_multi)
        else:
            encrypted_multi = 1
        encrypted_frequencies = [x * encrypted_multi for x in encrypted_frequencies]
        encrypted_coords = self.cal_graph(width, height // 2, encrypted_frequencies)
        objects = canvas.find_all()
        if event:
            plaintext_frequencies = sorted(self.constants.letter_frequencies.items(), key=lambda e: e[0])
            plaintext_frequencies = [x[1] * plaintext_multi for x in plaintext_frequencies]
            plaintext_coords = self.cal_graph(width, height, plaintext_frequencies)

        if objects:
            for i, obj in enumerate(objects[len(objects) // 2:]):
                canvas.coords(obj, *encrypted_coords[i])
            if event:
                for i, obj in enumerate(objects[:len(objects) // 2]):
                    canvas.coords(obj, *plaintext_coords[i])

        elif event:
            color = self.constants.theme['CTkButton']['fg_color'][self.constants.mode]
            for coords in plaintext_coords:
                canvas.create_rectangle(*coords)
            for coords in encrypted_coords:
                canvas.create_rectangle(*coords, outline=color)
        
    def cal_graph(self, width, height, frequencies):
        width -= 3
        alphabet_length = len(self.constants.alphabet)
        padding = 2
        space = alphabet_length * padding

        coords = []
        bar_width = (width - space) // alphabet_length
        bar_extra = (width - space) % alphabet_length
        bar_space = padding + bar_width
        for i in range(alphabet_length):
            bar_height = frequencies[i]
            coords.append((i * (bar_space) + padding + min(i, bar_extra),
                           height - 3,
                           i * (bar_space) + padding + bar_width + min(i + 1, bar_extra),
                           height - bar_height - 4))
        
        return coords

    def tab_select(self):
        index = int(self.tabview.get())
        if index != self.updated:
            self.update_graph(None)

    def update_widgets(self, frequencies):
        if not self.encode.get():
            self.frequencies = frequencies
            self.updated = int(self.tabview.get())
            self.update_graph(None)

    @staticmethod
    def update(text, constants, encode, mode, keyword_length, keyword_contents):
        if len(text) >= keyword_length:
            frequencies = []
            for i in range(keyword_length):
                split = ''.join([text[j] for j in range(i, len(text), keyword_length)]).lower()
                frequencies.append([split.count(letter) / len(split) for letter in constants.alphabet])
        else:
            frequencies = [[0] * len(constants.alphabet)] * keyword_length

        if mode:
            cal_char = lambda char, key: key - char
        elif encode:
            cal_char = lambda char, key: char + key
        else:
            cal_char = lambda char, key: char - key
        
        result = ''
        for index, letter in enumerate(text):
            if letter.lower() in constants.alphabet:
                char = constants.alphabet.index(letter.lower())
                key = constants.alphabet.index(keyword_contents[index % keyword_length].lower())
                new_letter = constants.alphabet[cal_char(char, key) % 26]

                if encode:
                    new_letter = new_letter.upper()
                result += new_letter
            else:
                result += letter
        return (result, (frequencies,))

    def display(self):
        if self.encode.get():
            self.frame.rowconfigure(0, weight=1)
            self.frame.rowconfigure(1, weight=1)
            self.frame.columnconfigure(0, weight=1)
            self.kw_label.grid(column=0, row=0, sticky='S')
            self.raw_kw_input.grid(column=0, row=1, sticky='N')
            self.encode_switch.grid(column=0, row=2, padx=15, pady=15, sticky='SE')
        else:
            self.frame.rowconfigure(4, minsize=100)
            self.frame.rowconfigure(7, weight=1)
            self.frame.columnconfigure(1, weight=1)
            self.kw_len_label.grid(column=0, row=0)
            self.kw_len_input.grid(column=0, row=1, pady=15)
            self.kw_label.grid(column=0, row=2, pady=15)
            self.kw_input.grid(column=0, row=3)
            self.radio_vigenere.grid(column=0, row=5, padx=25, pady=6, sticky='W')
            self.radio_beaufort.grid(column=0, row=6, padx=25, pady=6, sticky='W')
            self.tabview.grid(column=1, row=0, rowspan=8, padx=15, pady=5, sticky='NESW')
            self.encode_switch.grid(column=1, row=8, padx=15, pady=15, sticky='SE')
            self.kw_label.focus()

class RailFence(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.encode =  tk.IntVar(value=0)
        self.key = tk.StringVar(value='2')
        self.mode = tk.IntVar(value=0)
        self.mode.trace('w', self.mode_update)
        self.key.trace('w', self.input_update)
        self.encode.trace('w', self.encode_update)
        self.update_vars = [0, 2, self.vertical_counter, self.row_lengths]

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.key_label = ctk.CTkLabel(frame, font=font, text=self.texts['key'])
        self.key_input = ctk.CTkEntry(frame, font=font, justify='center', width=30,
                                      textvariable=self.key)
        self.vertical_radio = ctk.CTkRadioButton(frame, text=self.texts['vertical'], value=0,
                                                 variable=self.mode)
        self.horizontal_radio = ctk.CTkRadioButton(frame, text=self.texts['horizontal'], value=1,
                                                 variable=self.mode)
        self.encode_switch = ctk.CTkSwitch(frame, variable=self.encode, text=self.texts['encode'],
                                           font=self.font)
        self.key_input.bind('<MouseWheel>', self.scroll_input)

    def scroll_input(self, event):
        self.key.set(str(max(min(self.update_vars[1] + event.delta // 120, 30), 2)))

    def input_update(self, *args):
        value = self.key.get()
        if value.isnumeric():
            value = int(value)
            if 1 < value and value < 30:
                self.update_vars[1] = value
                self.update_output(self)

    def encode_update(self, *args):
        self.update_vars[0] = self.encode.get()
        self.update_output(self)

    def mode_update(self, *args):
        if self.mode.get():
            self.update_vars[2] = self.horizontal_counter
        else:
            self.update_vars[2] = self.vertical_counter

        self.update_output(self)

    @staticmethod
    def row_lengths(length, rails):
        cycle_length = rails * 2 - 2
        rail_lengths = [0, (length - 1) // cycle_length + 1]
        for i in range(rails - 2):
            rail_length = length // cycle_length * 2
            if length % cycle_length > i + 1:
                rail_length += 1
            if length % cycle_length > cycle_length - i - 1:
                rail_length += 1
            rail_lengths.append(rail_lengths[i + 1] + rail_length)

        return rail_lengths
 
    @staticmethod
    def vertical_counter(rails):
        rail_length = len(rails)
        cycle_length = rail_length * 2 - 2
        i = 0
        cycle = 0
        rail = 0
        while True:
            if rail == 0 or rail == rail_length - 1:
                yield rails[rail] + i // cycle_length
            else:
                yield rails[rail] + i // (rail_length - 1)

            i += 1
            cycle = i % cycle_length
            rail = cycle - 2 * (cycle // rail_length) * (cycle % rail_length + 1)

    @staticmethod
    def horizontal_counter(rails):
        rail_length = len(rails)
        cycle_length = rail_length * 2 - 2
        i = 0
        j = 0
        rail = 0
        while True:
            yield j

            if rail == 0 or rail == rail_length - 1:
                print(rail)
                j += cycle_length
            else:
                j += rail_length - 1
                if i % 2 == 1:
                    j += int(((rail_length - 1) / 2 - rail) * 2)
            
            i += 1
            print(i, rails)
            new_rail = next(x - 1 for x, y in enumerate(rails) if y > i)
            if new_rail != rail:
                rail = new_rail
                j = new_rail
                i = 0

    @staticmethod
    def update(text, constants, encode, rows, looping_counter, row_lengths):
        length = len(text)
        counter = looping_counter(row_lengths(length, rows))

        if encode:
            result = [''] * length
            for i in range(length):
                result[next(counter)] = text[i].upper()
            result = ''.join(result)
        else:
            result = ''
            for i in range(length):
                next(counter)
                #result += text[next(counter)].lower()

        return (result, ())

    def display(self):
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(3, minsize=12)
        self.frame.rowconfigure(6, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.key_label.grid(column=0, row=1, pady=0, sticky='S')
        self.key_input.grid(column=0, row=2, pady=12, sticky='N')
        self.vertical_radio.grid(column=0, row=4, pady=12, sticky='S')
        self.horizontal_radio.grid(column=0, row=5, pady=0, sticky='N')
        self.encode_switch.grid(column=0, row=6, padx=15, pady=15, sticky='SE')

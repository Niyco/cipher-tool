from defined import Stage
from stages_text import Spaces
import tkinter as tk
import customtkinter as ctk
import pickle
import base64
import random
import math
import time

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
                               fg=constants.theme['color']['text'][self.constants.mode], width=40, state='disabled',
                               insertbackground=self.constants.theme['color']['text'][self.constants.mode],
                               selectbackground=self.constants.theme['color']['entry'][self.constants.mode])
        self.scrollbar = ctk.CTkScrollbar(frame, command=self.textbox.yview, hover=False)
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

        self.textbox.configure(state='normal')
        self.textbox.delete(1.0, 'end')
        self.textbox.insert(1.0, formatted)
        self.textbox.configure(state='disabled')

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
        self.scrollbar.grid(column=2, row=0, pady=80, rowspan=4, sticky='NSW')

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

class SubstitutionFinder(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.results_var = tk.IntVar(value=10)
        self.iterations_var = tk.IntVar(value=10000)
        self.results_var.trace('w', self.input_update)
        self.iterations_var.trace('w', self.input_update)
        self.update_vars.extend([10, 10000, 0, Spaces.update])
        
    def setup(self, frame, constants):
        super().setup(self, frame, constants)
        self.results_label = ctk.CTkLabel(frame, text=(self.texts['results_label']
                                                       + ' ' + str(self.results_var.get())))
        self.iterations_label = ctk.CTkLabel(frame, text=(self.texts['iterations_label'] + ' '
                                                          + str(self.iterations_var.get())))
        self.results_slider = ctk.CTkSlider(frame, from_=1, to=26, number_of_steps=25, variable=self.results_var)
        self.iterations_slider = ctk.CTkSlider(frame, from_=10000, to=100000, number_of_steps=9,
                                               variable=self.iterations_var)
        self.update_button = ctk.CTkButton(frame, text=self.texts['update_button'], command=self.update_button)
        self.textbox = tk.Text(frame, bd=0, bg=self.constants.theme['color']['entry'][self.constants.mode],
                               fg=constants.theme['color']['text'][self.constants.mode], width=12, state='disabled',
                               insertbackground=self.constants.theme['color']['text'][self.constants.mode],
                               selectbackground=self.constants.theme['color']['entry'][self.constants.mode])
        self.textbox.bind('<Control-c>', self.copy)
        self.scrollbar = ctk.CTkScrollbar(frame, command=self.textbox.yview, hover=False, height=350)
        self.textbox.configure(yscrollcommand=self.scrollbar.set)

        self.update_widgets({char.upper(): '' for char in self.constants.alphabet[:self.results_var.get()]})

    def copy(self, event):
        value = base64.b64encode(pickle.dumps(self.substitutions))
        self.frame.master.clipboard_clear()
        self.frame.master.clipboard_append(value.decode('utf-8'))
        self.frame.master.update()
    
    def update_button(self):
        self.update_vars[2] = 1
        self.update_output(self)
        self.update_vars[2] = 0
    
    def input_update(self, var_name, index, mode):
        if var_name == str(self.results_var):
            self.update_vars[0] = self.results_var.get()
            self.results_label.configure(text=(self.texts['results_label'] + ' '
                                               + str(self.results_var.get())))
            self.update_widgets({char.upper(): '' for char in self.constants.alphabet[:self.results_var.get()]})
        else:
            self.update_vars[1] = self.iterations_var.get()
            self.iterations_label.configure(text=(self.texts['iterations_label'] + ' '
                                                  + str(self.iterations_var.get())))

        self.update_output(self)
    
    @staticmethod
    def update(text, constants, results, iterations, update, spaces_function):
        text = ''.join([char for char in text if char.lower() in constants.alphabet + [' ']])
        if update and len(text.replace(' ', '')) > 1:
            
            shortend_text = text[:1350]
            
            def generate_alphabet(alphabet):
                pos_1 = random.randrange(len(sample_alphabet))
                pos_2 = random.sample([i for i in range(len(alphabet)) if i != pos_1], 1)[0]
                alphabet[pos_1], alphabet[pos_2] = alphabet[pos_2], alphabet[pos_1]
                
                return alphabet

            def score(alphabet):
                subs = {char: alphabet[index] for index, char in enumerate(sample_alphabet)}
                score = math.prod([(english_bigrams[subs[bigram[0]] + subs[bigram[1]]]
                                    * 1.68 ** count) for bigram, count in bigrams])
                
                return score

            def best_scores(amount):
                best_scores = [0]
                prev_score = 0
                best_alphabets = [constants.alphabet]
                prev_alphabet = constants.alphabet
                new_alphabet = constants.alphabet
                for i in range(int(iterations / 2)):
                    new_score = score(new_alphabet)
                    if new_score > best_scores[0]:
                        best_scores.insert(0, new_score)
                        best_alphabets.insert(0, new_alphabet.copy())
                        best_scores = best_scores[:amount]
                        best_alphabets = best_alphabets[:amount]
                        prev_alphabet = new_alphabet.copy()
                        prev_score = new_score
                        
                    elif new_score > prev_score or random.uniform(0, prev_score) <= new_score:
                        prev_alphabet = new_alphabet.copy()
                        prev_score = new_score
                        
                    else:
                        new_alphabet = prev_alphabet.copy()

                    new_alphabet = generate_alphabet(new_alphabet)

                best_subs = []
                for i in range(amount):
                    best_subs.append(dict(sorted([(char.upper(), best_alphabets[i][index]) for index,
                                                  char in enumerate(sample_alphabet)], key=lambda e:e[0])))

                return best_subs, best_scores
            
            english_bigram_normalizer = 1 / max([bigram[1] for bigram in constants.bigram_frequencies.items()])
            english_bigrams = {k: v * english_bigram_normalizer for k, v in constants.bigram_frequencies.items()}
            bigrams = {}
            for word in shortend_text.split(' '):
                for i in range(len(word) - 1):
                    bigram = word[i:i + 2]
                    if bigram in bigrams:
                        bigrams[bigram] += 1
                    else:
                        bigrams[bigram] = 1
            bigrams = sorted(bigrams.items(), key=lambda e: e[1], reverse=True)
            sample_alphabet = set()
            for bigram in bigrams:
                sample_alphabet.update(bigram[0])

            candidates = best_scores(3)[0]
            candidates.extend(best_scores(3)[0])

            scores = []
            for candidate in candidates:
                decoded = ''
                for letter in text:
                    if letter.upper() in candidate:
                        decoded += candidate[letter.upper()]
                    else:
                        decoded += letter
                scores.append(spaces_function(decoded, constants, 2, return_score=True))
            
            best_subs = candidates[scores.index(max(scores))]
            return (best_subs,)
        
        else:
            return (None,)

    def update_widgets(self, best_subs):
        if best_subs != None:
            self.substitutions = best_subs
            arrow = '->'
            formatted = '\n'.join([f'\'{k}\' {arrow} \'{v}\'' for k, v in best_subs.items()])

            self.textbox.configure(state='normal')
            self.textbox.delete(1.0, 'end')
            self.textbox.insert(1.0, formatted)
            self.textbox.configure(state='disabled')

    def display(self):
        self.frame.columnconfigure(0, minsize=30)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.results_label.grid(row=0, column=1, pady=4, sticky='S')
        self.results_slider.grid(row=1, column=1, pady=10, sticky='')
        self.iterations_label.grid(row=2, column=1, pady=4, sticky='')
        self.iterations_slider.grid(row=3, column=1, pady=10, sticky='')
        self.update_button.grid(row=4, column=1, pady=50, sticky='N')
        self.textbox.grid(row=0, column=2, rowspan=5, pady=120)
        self.scrollbar.grid(row=0, column=3, rowspan=5, pady=120, sticky='')

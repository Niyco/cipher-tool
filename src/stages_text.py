from src.defined import Stage, CustomSlider
import tkinter as tk
import customtkinter as ctk
import math

class UpperCase(Stage):
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        
    @staticmethod
    def update(text, constants):
        return (text.upper(), ())
    
class LowerCase(Stage):
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        
    @staticmethod
    def update(text, constants):
        return (text.lower(), ())

class Reverse(Stage):
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        
    @staticmethod
    def update(text, constants):
        return (text[::-1], ())

class Strip(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.spaces_var = tk.IntVar()
        self.spaces_var.set(1)
        self.update_vars.append(1)
        
    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.checkbox = ctk.CTkCheckBox(frame, text=self.texts['checkbox'], variable=self.spaces_var,
                                        command=self.checkbox_update, font=self.font)

    def checkbox_update(self):
        self.update_vars[0] = bool(self.spaces_var.get())
        self.update_output(self)

    @staticmethod
    def update(text, constants, spaces):
        if spaces:
            stripped = ''.join([c for c in text if c.lower() in constants.alphabet])
        else:
            stripped = ''.join([c for c in text if c.lower() in constants.alphabet + [' ']])
            
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
        self.update_vars.append(5)

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.label = ctk.CTkLabel(frame, text=self.texts['label'], font=self.font)
        self.input = ctk.CTkEntry(frame, textvariable=self.block_length_var, width=30,
                                  justify='center', font=self.font)
        self.input.bind('<MouseWheel>', self.input_scroll)

    def input_update(self, var, index, mode):
        value = self.block_length_var.get()
        if value.isnumeric() and value != '0':
            self.update_vars[0] = int(value)
        self.update_output(self)

    def input_scroll(self, event):
        if event.delta > 0:
            new = self.update_vars[0] + 1
        else:
            new = max(self.update_vars[0] - 1, 1)
        self.block_length_var.set(str(new))

    @staticmethod
    def update(text, constants, block_length):
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
        self.label.grid(row=0, column=0, sticky='E', padx=8)
        self.input.grid(row=0, column=1, sticky='W')

class Spaces(Stage):
    def __init__(self, update_output):
        super().__init__(update_output)
        self.complexity_var = tk.IntVar()
        self.complexity_var.set(2)
        self.update_vars.append(2)

    def setup(self, frame, constants, font):
        super().setup(self, frame, constants, font)
        self.slider = CustomSlider(frame, number_of_steps=4, variable=self.complexity_var,
                                   from_=1, to=5, var_cb=self.input_update)
        self.label = ctk.CTkLabel(frame, text=self.texts['label'], font=self.font)

    def input_update(self, variable, value):
        self.update_vars[0] = value
        self.update_output(self)

    @staticmethod
    def update(text, constants, complexity, return_score=False):
        complexity += 1
        
        def cal_score(word):
            if word.lower() in constants.word_frequencies:
                word_frequency = math.log(constants.word_frequencies[word.lower()], 10) + 6
            else:
                word_frequency = 0

            return word_frequency * (len(word) ** 2)

        def cal_best_path(text_index, complexity):
            paths = []
            factorial = math.factorial(complexity)
            length = factorial
            
            for x in range(factorial):
                paths.append([[x // (factorial // complexity)]])
            factorial = factorial // complexity
            for y in range(complexity - 1, 1, -1):
                for z in range(length):
                    paths[z][0].append(z // (factorial // y) % y)
                factorial = factorial // y
                
            for path in paths:
                score = 0
                index = text_index
                for location in path[0]:
                    if index == string_length or location >= len(best_scores[index]):
                        break
                    score += best_scores[index][location][0]
                    index += best_scores[index][location][1]
                path.append(score)

            return max(paths, key=lambda e: e[1])[0]

        final_string = ''
        score = 0
        for string in text.split(' '):
            string = ''.join([c for c in string if c.lower() in constants.alphabet + ['\'']])
            string_length = len(string)
            
            best_scores = [None] * (string_length)
            
            for index in range(string_length + 1):
                for length in range(1, min(constants.max_word_length, string_length - index + 1)):
                    score = cal_score(string[index:index + length])
                    if best_scores[index]:
                        best_scores[index].append((score, length))
                    else:
                        best_scores[index] = [(score, length)]
            
            for index in best_scores:
                index.sort(reverse=True, key=lambda e: e[0])

            split_string = ''
            index = 0
            while index < string_length:
                path = cal_best_path(index, min(complexity, string_length - index))
                split_string += string[index:index + best_scores[index][path[0]][1]] + ' '
                score += best_scores[index][path[0]][0]
                index += best_scores[index][path[0]][1]

            final_string += split_string
        if return_score:
            return score
        return (final_string, ())

    def display(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.label.grid(row=0, column=0, sticky='S')
        self.slider.grid(row=1, column=0, sticky='N')

import customtkinter as ctk
import darkdetect
import json
import sys

class DisplayText(ctk.CTkTextbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def textbox_click(event):
            self.focus()
            return 'break'

        self.bind('<Motion>', lambda event: 'break')
        self.bind('<Leave>', lambda event: 'break')
        self.bind('<ButtonPress-1>', textbox_click)

class CustomSlider(ctk.CTkSlider):
    def __init__(self, *args, **kwargs):
        variable = kwargs['variable']
        self.slider_cb, self.prev_value, self.var_cb, self.loop = None, None, None, False
        if 'slider_cb' in kwargs:
            self.slider_cb = kwargs.pop('slider_cb')
        if 'var_cb' in kwargs:
            self.var_cb = kwargs.pop('var_cb') 
        if 'loop' in kwargs:
            self.loop = kwargs.pop('loop')

        super().__init__(*args, **kwargs)

        if self.slider_cb:
            self.prev_value = variable.get()
            variable.trace('w', self.var_trace)
        if self.var_cb: 
            self.bind('<ButtonRelease-1>', lambda event: self.var_cb(variable, variable.get()))
        self.bind('<MouseWheel>', self.scroll)

    def scroll(self, event):
        if self.loop and self._variable.get() == self._to and event.delta < 0:
            new = self._from_
        elif self.loop and self._variable.get() == self._from_ and event.delta > 0:
            new = self._to
        else:
            change = event.delta // 120 * (self._to - self._from_) // self._number_of_steps
            new = max(min(self._variable.get() - change, self._to), self._from_)
        self._variable.set(new)
        if self.var_cb:
            self.var_cb(self._variable, self._variable.get())
        
    def var_trace(self, *args):
        self.new_value = self._variable.get()
        if self.new_value != self.prev_value:
            self.prev_value = self.new_value
            self.slider_cb(self._variable, self.prev_value)

class Stage:
    def __init__(self, update_output):
        self.update_output = update_output
        self.update_vars = []

    def setup(self, child, frame, constants, font):
        self.frame = frame
        self.constants = constants
        self.font = font
        self.texts = constants.lang['stage_' + type(child).__name__.lower()]
        
    @staticmethod
    def update(text, constants):
        return ((), ())

    def update_widgets(self):
        pass
    
    def display(self):
        pass

class Constants:
    theme_path = r'themes/'
    lang_path = r'lang/'
    modes = ('light', 'dark')
    default_size ='1366x768'
    min_size = '672x378'
    check_queue_delay = 100
    font_change_delay = 180
    toolbar_step = 12
    toolbar_updates = 0
    toolbar_delay = 12
    stages_drag_max = 8
    loading_delay = 50
    threaded = True
    mode_name = 'default'
    theme_name = 'blue'
    lang_name = 'en'
    morse_codes = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g', '....': 'h',
           '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o', '.--.': 'p',
           '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x',
           '-.--': 'y', '--..': 'z', '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
           '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'}
    binary_codes = {'00000': 'a', '00001': 'b', '00010': 'c', '00011': 'd', '00100': 'e', '00101': 'f', '00110': 'g',
                    '00111': 'h', '01000': 'i', '01001': 'j', '01010': 'k', '01011': 'l', '01100': 'm', '01101': 'n',
                    '01110': 'o', '01111': 'p', '10000': 'q', '10001': 'r', '10010': 's', '10011': 't', '10100': 'u',
                    '10101': 'v', '10110': 'w', '10111': 'x', '11000': 'y', '11001': 'z'}
    baconian_codes = {'aaaaa': 'a', 'aaaab': 'b', 'aaaba': 'c', 'aaabb': 'd', 'aabaa': 'e', 'aabab': 'f', 'aabba': 'g',
                    'aabbb': 'h', 'abaaa': 'i', 'aabaaa': 'j', 'abaab': 'k', 'ababa': 'l', 'ababb': 'm', 'abbaa': 'n',
                    'abbab': 'o', 'abbba': 'p', 'abbbb': 'q', 'baaaa': 'r', 'baaab': 's', 'baaba': 't', 'abaabb': 'u',
                    'baabb': 'v', 'babaa': 'w', 'babab': 'x', 'babba': 'y', 'babbb': 'z'}
    baudot_codes = {'00000': ('', ''), '01000': ('\n', '\n'), '00010': ('\n', '\n'), '00100': (' ', ' '),
                    '10111': ('q', '1'), '10011': ('w', '2'), '00001': ('e', '3'), '01010': ('r', '4'),
                    '10000': ('t', '5'), '10101': ('y', '6'), '00111': ('u', '7'), '00110': ('i', '8'),
                    '11000': ('o', '9'), '10110': ('p', '0'), '00011': ('a', '-'), '00101': ('s', '\''),
                    '01001': ('d', 'WRU?'), '01101': ('f', '!'), '11010': ('g', '&'), '10100': ('h', '$'),
                    '01011': ('j', 'BELL'), '01111': ('k', '('), '10010': ('l', ')'), '10001': ('z', '+'),
                    '11101': ('x', '/'), '01110': ('c', ':'), '11110': ('v', '='), '11001': ('b', '?'),
                    '01100': ('n', ','), '11100': ('m', '.'), '11011': ('FS', 'FS'), '11111': ('LS', 'LS')}
    inverses = {1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19, 15: 7, 17: 23, 19: 11, 21: 7, 23: 17, 25: 25}
    
    theme = None
    lang = None
    os = None
    mode = None
    letter_frequencies = None
    language_ioc = None
    alphabet = None
    bigram_frequencies = None
    min_word_frequency = None
    max_word_length = None
    word_frequencies = None
    
    def load(self):
        theme_file = open(self.theme_path + self.theme_name + '.json', encoding='utf-8')
        self.theme = json.load(theme_file)
        theme_file.close()
        lang_file = open(self.lang_path + 'lang_' + self.lang_name + '.json', encoding='utf-8')
        self.lang = json.load(lang_file)
        lang_file.close()
        freq_file = open(self.lang_path + 'freq_' + self.lang_name + '.json', encoding='utf-8')
        freq_data = json.load(freq_file)
        freq_file.close()

        if sys.platform.startswith('darwin'): self.os = 'macOS'
        elif sys.platform.startswith('win'): self.os = 'Windows'
        elif sys.platform.startswith('linux'): self.os = 'Linux'
        if self.mode_name == 'light': self.mode = 0
        elif self.mode_name == 'dark': self.mode = 1
        else: self.mode = self.modes.index(darkdetect.theme().lower())

        self.letter_frequencies = freq_data['letters']
        self.language_ioc = sum([self.letter_frequencies[x] ** 2 for x in self.letter_frequencies])
        self.alphabet = list(sorted(self.letter_frequencies.keys()))
        self.bigram_frequencies = freq_data['bigrams']
        self.min_word_frequency = 10 ** ((0 - len(freq_data['words']) + 1) / 100)
        self.max_word_length = 0
        self.word_frequencies = {}
        for index, bucket in enumerate(freq_data['words']):
            freq = 10 ** (-index / 100)
            for word in bucket:
                length = len(word)
                if length > self.max_word_length:
                    self.max_word_length = length
                self.word_frequencies[word] = freq

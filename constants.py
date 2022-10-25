import darkdetect
import json
import sys

theme_path = r'themes/'
lang_path = r'lang/'
modes = ['light', 'dark']
default_size ='1366x768'
min_size = '672x378'
check_queue_delay = 100
toolbar_step = 12
toolbar_updates = 0
toolbar_delay = 12
stages_drag_max = 8
loading_delay = 50
threaded = False
mode_name = 'default'
theme_name = 'dark-blue'
lang_name = 'en'

class Stage:
    def __init__(self, update_output):
        self.update_output = update_output
        self.update_vars = ()

    def setup(self, frame, texts):
        self.frame = frame
        self.texts = texts
        
    @staticmethod
    def update(text):
        return ((), ())

    def update_widgets(self):
        pass
    
    def display(self):
        pass

def load_constants():
    global os, mode, theme, lang, letter_frequencies, word_frequencies, alphabet
    global min_word_frequency, max_word_length, language_ioc

    theme_file = open(theme_path + theme_name + '.json')
    theme = json.load(theme_file)
    theme_file.close()
    lang_file = open(lang_path + 'lang_' + lang_name + '.json')
    lang = json.load(lang_file)
    lang_file.close()
    freq_file = open(lang_path + 'freq_' + lang_name + '.json')
    freq_data = json.load(freq_file)
    freq_file.close()
    
    if sys.platform.startswith('darwin'): os = 'macOS'
    elif sys.platform.startswith('win'): os = 'Windows'
    elif sys.platform.startswith('linux'): os = 'Linux'
    if mode_name == 'light': mode = 0
    elif mode_name == 'dark': mode = 1
    else: mode = modes.index(darkdetect.theme().lower())
    
    letter_frequencies = freq_data['letters']
    language_ioc = sum([letter_frequencies[x] ** 2 for x in letter_frequencies])
    alphabet = list(letter_frequencies.keys())
    min_word_frequency = 10 ** ((0 - len(freq_data['words']) + 1) / 100)
    max_word_length = 0
    word_frequencies = {}
    for index, bucket in enumerate(freq_data['words']):
        freq = 10 ** (-index / 100)
        for word in bucket:
            length = len(word)
            if length > max_word_length:
                max_word_length = length
            word_frequencies[word] = freq

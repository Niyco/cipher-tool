import json

theme_path = r'themes/'
lang_path = r'lang/'
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

    def setup(self, frame):
        self.frame = frame

    @staticmethod
    def update(text): # Update_vars passed here
        return ((), ())

    def update_widgets(self): # Return from update passed here
        pass
    
    def display(self):
        pass

_lang_file = open(lang_path + 'lang_' + lang_name + '.json')
lang = json.load(_lang_file)
_lang_file.close()
_freq_file = open(lang_path + 'freq_' + lang_name + '.json')
_freq_data = json.load(_freq_file)
_freq_file.close()
letter_frequencies = _freq_data['letters']
alphabet = list(letter_frequencies.keys())
min_word_frequency = 10 ** ((0 - len(_freq_data['words']) + 1) / 100)
max_word_length = 0
word_frequencies = {}
for _index, _bucket in enumerate(_freq_data['words']):
    _freq = 10 ** (-_index / 100)
    for _word in _bucket:
        _length = len(_word)
        if _length > max_word_length:
            max_word_length = _length
        word_frequencies[_word] = _freq

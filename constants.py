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
mode_name = 'default'
theme_name = 'green'
lang_name = 'lang_en'

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

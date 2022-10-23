theme_path = r'themes'
lang_path = r'lang'
path_window_icon = r'resources\icon.png'
path_stage_remove = r'resources\stage_remove.png'
path_stage_shown = r'resources\stage_shown.png'
path_stage_hidden = r'resources\stage_hidden.png'
path_stage_up = (r'resources\stage_up_light.png', r'resources\stage_up_dark.png')
path_stage_down = {'green': [r'resources\stage_down_light_1.png', r'resources\stage_down_dark_1.png'],
                   'blue': [r'resources\stage_down_light_2.png', r'resources\stage_down_dark_2.png'],
                   'dark-blue': [r'resources\stage_down_light_3.png', r'resources\stage_down_dark_3.png']}
path_toolbar_icon = r'resources\toolbar.png'
path_toolbar_stage = [r'resources\toolbar_stage_light.png', r'resources\toolbar_stage_dark.png']
path_toolbar_separator = r'resources\toolbar_separator.png'
path_toolbar_increase = [r'resources\toolbar_increase_light.png', r'resources\toolbar_increase_dark.png']
path_toolbar_decrease = [r'resources\toolbar_decrease_light.png', r'resources\toolbar_decrease_dark.png']
path_toolbar_copy = [r'resources\toolbar_copy_light.png', r'resources\toolbar_copy_dark.png']
path_toolbar_clear = [r'resources\toolbar_clear_light.png', r'resources\toolbar_clear_dark.png']
path_toolbar_theme = [r'resources\toolbar_theme_light.png', r'resources\toolbar_theme_dark.png']
path_toolbar_options = [r'resources\toolbar_options_light.png', r'resources\toolbar_options_dark.png']
path_loading_animation = [r'resources\loading_light.gif', r'resources\loading_dark.gif']

color_deselected = ['#BBBBBB', '#4C4C4C']
default_size ='1366x768'
min_size = '672x378'

check_queue_delay = 100
hover_color_change_toolbar = -20
hover_color_change_stage = -8
toolbar_step = 8
toolbar_delay = 0
stage_spaceing = 4
stages_drag_max = 8
loading_delay = 0.05

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

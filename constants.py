theme_path = r'customtkinter\assets\themes\green.json'
lang_path = r'lang\lang_en.json'
icon_path = r'resources\icon.png'
toolbar_icon_path = r'resources\toolbar.png'
mode = 'dark'
theme = 'green'
radio_selected_color = '#121212'
default_size ='1366x768'
min_size = '608x342'
hover_color_change = -20
toolbar_size = 75
toolbar_step = 5
toolbar_animation_time = 50

class AnalysisStage:
    def __init__(self, frame, update):
        self.update = update
    def analyse(self, text):
        pass
    def display(self):
        pass

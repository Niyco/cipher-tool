lang_path = r'lang.json'
icon_path = r'resources\icon.png'
toolbar_icon_path = r'resources\toolbar.png'
mode = 'dark'
default_size ='1366x768'
min_size = '576x324'
hover_color_change = -20
toolbar_size = 75
toolbar_animation_time = 100

class AnalysisStage:
    def __init__(self, frame, update): # Create all widgets
        self.update = update
    def analyse(self, text): # Analyse text and update widget content
        pass
    def display(self): # Show all widgets (grid/pack/place)
        pass

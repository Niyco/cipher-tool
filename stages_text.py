from constants import *

class UpperCase(Stage):
    @staticmethod
    def update(text):
        return (text.upper(), ())
    
class LowerCase(Stage):
    @staticmethod
    def update(text):
        return (text.lower(), ())

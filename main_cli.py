import ctypes

ctools = ctypes.CDLL("build\\ctools.dll")
ctools.caesar_encode.argtypes = [ctypes.c_char_p, ctypes.c_int]

print(ctools.caesar_encode("Text".encode('utf-8'), 5))
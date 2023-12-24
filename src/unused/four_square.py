encrypt = ''
plaintext_square = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
keysquare_1 = []
keysquare_2 = []

def get_coords(letter, square):
    pos = square.index(letter)
    return (pos % 5, pos // 5)

def get_letter(coords, square):
    x, y = coords
    return square[y * 5 + x]

plaintext = ''
for i in range(0, len(encrypt), 2):
    x1, y1 = get_coords(encrypt[i], keysquare_1)
    x2, y2 = get_coords(encrypt[i + 1], keysquare_2)

    plaintext += get_letter((x2, y1), plaintext_square)
    plaintext += get_letter((x1, y2), plaintext_square)
print(plaintext)

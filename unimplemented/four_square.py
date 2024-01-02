_plaintext_square = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def _get_coords(letter, square):
    pos = square.index(letter)
    return (pos % 5, pos // 5)

def _get_letter(coords, square):
    x, y = coords
    return square[y * 5 + x]

def decrypt(ciphertext, keysquare_1, keysquare_2):
    plaintext = []
    for i in range(0, len(ciphertext), 2):
        x1, y1 = _get_coords(ciphertext[i], keysquare_1)
        x2, y2 = _get_coords(ciphertext[i + 1], keysquare_2)

        plaintext.append(_get_letter((x2, y1), _plaintext_square))
        plaintext.append(_get_letter((x1, y2), _plaintext_square))
    return ''.join(plaintext)
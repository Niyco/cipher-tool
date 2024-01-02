import string

cipher_alphabet = {string.ascii_uppercase[i]: i for i in range(26)}

def encrypt(ciphertext, key):
    matrix_size = len(key)
    plaintext = []
    block = []
    for i, letter in enumerate(ciphertext, 1):
        block.append(cipher_alphabet[letter])
        if i % matrix_size == 0:
            for row in key:
                plaintext.append(string.ascii_lowercase[int(sum([row[j] * block[j] for j in range(matrix_size)]) % 26)])
            block.clear()
    return ''.join(plaintext)
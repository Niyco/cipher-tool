import string

'''
def cal_score(text):
    text_length = len(text)
    freqs = {bigram: 0 for bigram in bigram_frequencies}
    for i in range(text_length):
        bigram = text[i - 1:i + 1]
        if len(bigram) == 2: freqs[bigram] += 1

    return math.sqrt(sum([(freqs[bigram] / text_length - value) ** 2 for bigram, value in bigram_frequencies.items()]) / len(bigram_frequencies))
'''

ciphertext = ''
matrix_size = 2

decryption_key = [(), ()]

plaintext = ''
for i in range(0, len(ciphertext), matrix_size):
    letter_matrix = [string.ascii_uppercase.index(letter.upper()) for letter in ciphertext[i:i + matrix_size]]
    for row in decryption_key:
        plaintext += string.ascii_lowercase[sum([row[j] * letter_matrix[j] for j in range(matrix_size)]) % 26]
print(plaintext)
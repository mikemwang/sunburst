"""A mapping of letters to colours"""

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def create_color_map(ALPHABET):
    incr = 1.0/28.0
    mapping = {}
    init = 0.95
    for letter in ALPHABET:
        mapping[letter]=init
        init-=incr
    return mapping

COLOUR_MAPPING = create_color_map(ALPHABET)




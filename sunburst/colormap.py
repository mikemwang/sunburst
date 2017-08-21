"""A mapping of letters to colours"""
from pyx import color

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
NUMBERS = "0123456789"

def sector_color_map(ALPHABET):
    incr = 1.0/(len(ALPHABET)+2)
    mapping = {}
    init = 1.0 - 0.5*(1.0-(len(ALPHABET)*incr))
    for letter in ALPHABET:
        mapping[letter] = color.rgb(init, init, init)
        init -= incr
    for number in NUMBERS:
        mapping[number] = color.rgb(0.5, 0.5, 0.5)
    mapping[''] = color.rgb.red
    return mapping


COLOR_MAPPING = sector_color_map(ALPHABET)

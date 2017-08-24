"""A mapping of letters to colours"""
from pyx import color


def color_map(alpha, nums):
    """returns a dict of which color a character maps to"""
    n = 1.0/(len(alpha)+5)
    mapping = {}
    init = len(alpha)*n
    for letter in alpha:
        mapping[letter] = color.rgb(init, init, init)
        init -= n
    for number in nums:
        mapping[number] = color.rgb(0.5, 0.5, 0.5)
    mapping[''] = color.rgb.red
    return mapping

#def color_map_2(alpha, nums):
#    """returns a dict of which color a character maps to"""
#    n = 1.0/(len(alpha)+5)
#    mapping = {}
#    init = len(alpha)*n
#    for letter in alpha:
#        mapping[letter] = color.rgb(init, init, init)
#        init -= n
#    for number in nums:
#        mapping[number] = color.rgb(0.5, 0.5, 0.5)
#    mapping[''] = color.rgb.red
#    return mapping

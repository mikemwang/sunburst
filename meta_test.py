"""test
multiline
docstring"""

import os

raw_file = open(os.path.basename(__file__), 'r')
raw_strings = []
for line in raw_file:
    # skip blank lines
    if line == '\n':
        continue
    # strip out newline char
    raw_strings.append(line[:-1])

for string in raw_strings:
    print string

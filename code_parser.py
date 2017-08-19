# test inline comment

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUMBERS = '123456789'

class CodeParser(object):
    """ a class that stores the logical paths of a program"""

    def __init__(self, source_file):
        """arguments:

        source_file: the name of the file to be analyzed

        """
        self.source = open(source_file, 'r')

    def parse(self):

        data = self.source
        data = self.remove_indents_and_newline(data)
        data = self.remove_comments(data)
        data = self.lowercase(data)
        data = self.split_strings(data)
        clean_data = self.format(data)
        return clean_data

    def format(self, clean_data):
        freq_dict = {}
        flipped = []
        freq_list = []

        for entry in clean_data:
            if entry not in freq_dict.keys():
                freq_dict[entry] = 1
                continue
            freq_dict[entry] += 1

        for entry in freq_dict:
            flipped.append({freq_dict[entry]:entry})

        for entry in flipped:
            for key in entry:
                freq_list.append((entry[key], key))

        return freq_list

    def remove_indents_and_newline(self, source):
        """take in the raw lines read in from the source file, strip out
        indentation and ending newline characters

        arguments:
            raw_source: the opened source code file

        """
        sanitized = []
        for line in source:
            while True:
                # strip out indentation and newline
                if line[0] == ' ':
                    line = line[1:]
                else:
                    break
            if line == '\n':
                continue
            else:
                sanitized.append(line[0:-1])

        return sanitized

    def remove_comments(self, source):
        """remove inline comments and docstrings"""
        sanitized = []
        in_docstring = False
        for line in source:
            save_line = True
            if line[0] == '#':
                continue
            if len(line) > 2:
                if line[0:3] == '"""' and not in_docstring:
                    in_docstring = True
                    save_line = False
                    if len(line)>5:
                        if line[-3:] == '"""':
                            in_docstring = False
                elif line[-3:] == '"""' and in_docstring:
                    in_docstring = False
                    save_line = False

            if save_line and not in_docstring:
                sanitized.append(line)
                print(line)

        return sanitized

    def lowercase(self, source):
        sanitized = []
        for line in source:
            sanitized.append(line.lower())
        return sanitized

    def split_strings(self, source):
        sanitized = []
        for line in source:
            temp_line = line
            cur_word = ''
            while temp_line:
                cur_letter = temp_line[0]
                if cur_letter in ALPHABET:
                    cur_word += cur_letter
                elif cur_letter in NUMBERS:
                    if cur_word != '':
                        cur_word += cur_letter
                elif cur_word != '':
                    sanitized.append(cur_word)
                    cur_word = ''
                temp_line = temp_line[1:]
        return sanitized

test = CodeParser('test.py')
results = test.parse()
print(results)

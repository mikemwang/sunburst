import os


def parse_source(source_dir, alphabet, numbers):
    clean_data = {}
    source = os.listdir(source_dir)
    for sourcef in source:
        # ignore hidden files and __init__
        if sourcef[0] == '.':
            continue
        if sourcef[0] == '_':
            continue
        if sourcef.endswith(".py"):
            cur_source = open(source_dir+'/'+sourcef, 'r')
            data = cur_source.readlines()
            for item in PARSE:
                data = item(data, alphabet, numbers)
            for entry in data:
                if entry in clean_data.keys():
                    clean_data[entry] += data[entry]
                else:
                    clean_data[entry] = data[entry]
    return clean_data

def parse_trace(trace_source, alphabet, numbers):
    clean_data = trace_source
    for item in PARSE:
        clean_data = item(clean_data, alphabet, numbers)
    return clean_data


def format_data(clean_data, _, __):
    freq_dict = {}

    for entry in clean_data:
        if entry not in freq_dict.keys():
            freq_dict[entry] = 1
            continue
        freq_dict[entry] += 1

    return freq_dict

def remove_indents_and_newline(source, _, __):
    """take in the raw lines read in from the source filestrip out
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
            if len(line)>0:
                sanitized.append(line[0:-1])
    return sanitized

def remove_comments(source, _, __):
    """remove inline comments and docstrings"""
    sanitized = []
    in_string = False
    for line in source:
        save_line = True
        if line[0] == '#':
            # don't add if it's a commentcontinue
            continue
        elif "#'" in line:
            # these lines are flagged to be ignored
            continue
        elif '#' in line:
            # don't add the latter half if line contains comment
            line = line.split('#')[0]
            continue
        # logic to check for docstrings
        if len(line) > 2:
            if line[0:3] == '"""' and not in_string:
                in_string = True
                save_line = False
                if len(line)>5:
                    if line[-3:] == '"""':
                        in_string = False
            elif line[-3:] == '"""' and in_string:
                in_string = False
                save_line = False
        if save_line and not in_string:
            sanitized.append(line)
    return sanitized

def lowercase(source, _, __):
    sanitized = []
    for line in source:
        sanitized.append(line.lower())
    return sanitized

def split_strings(source, alphabet, numbers):
    sanitized = []
    for line in source:
        temp_line = line
        cur_word = ''
        while temp_line:
            cur_letter = temp_line[0]
            if cur_letter in alphabet:
                cur_word += cur_letter
            elif cur_letter in numbers:
                if cur_word != '':
                    cur_word += cur_letter
            elif cur_word != '':
                sanitized.append(cur_word)
                cur_word = ''
            temp_line = temp_line[1:]
    return sanitized

def remove_underscores(source, _, __):
    sanitized = []
    for line in source:
        temp = []
        temp = line.split('_')
        line = ''
        for item in temp:
            line += item
        sanitized.append(line)
    return sanitized


PARSE = [
    remove_indents_and_newline,
    remove_comments,
    lowercase,
    split_strings,
    remove_underscores,
    format_data,
    ]

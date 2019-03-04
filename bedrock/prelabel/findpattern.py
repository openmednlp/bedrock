import re


def find_regex_pattern(regex, text):
    
    reg = re.compile(regex)

    vec = []
    match = []
    string = ''

    for el in re.finditer(reg, text):
        if el:
            indices = el.span()
            vec.append(indices)
            match.append(el.group())
            string = string + text[indices[0]:indices[1]] + ', '
    return vec, match

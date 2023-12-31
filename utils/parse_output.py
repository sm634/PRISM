import re


def parse_stringified_json(json_string):
    """
    Parses a stringified json output produced by GPT, then returns a python dictionary.
    :param json_string: the json contained within a string which needs to be cleaned.
    :return: A Dictionary
    """
    new_lines_removed = re.subn(pattern=r'\n\s+', repl='', string=json_string)[0]
    new_lines_removed = re.subn(pattern=r'\n', repl='', string=new_lines_removed)[0]
    string_json = new_lines_removed[new_lines_removed.index('{'):new_lines_removed.index('}')+1]
    output = eval(string_json)

    return output

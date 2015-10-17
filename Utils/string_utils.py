import re

__re_collapse_spaces__ = re.compile("\s+")
__re_remove_special_chars__ = re.compile("[;:\'\"\*/\),\(\|\s]+")

def collapse_spaces(s):
    return __re_collapse_spaces__.sub(" ", s).strip()

def clean_str(s):
    s = str(s).replace("'s"," ")
    #doesn't work in regex
    s = s.replace("-", " ").replace("\\"," ")
    s = __re_remove_special_chars__.sub(" ",s).strip()
    return collapse_spaces(s)

def strip_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)
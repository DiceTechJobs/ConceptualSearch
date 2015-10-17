# Solr-like analysis pipeline
# let's me replicate the solr processing within python
# so I can then do machine-learning on the output

from Utils.file_utils import load_stop_words
from collections import defaultdict

class SynonymMapper(object):
    def __init__(self, mapper, nested, case_sensitive=False):
        self.case_sensitive = case_sensitive
        self.mapper = mapper
        self.nested = nested
        self.synonyms = set()
        for rhs in self.mapper.values():
            for syn in rhs:
                self.synonyms.add(syn)

    def is_synonym(self, term):
        return term in self.synonyms

    def map_synonyms(self, tokens, debug=False):
        mapped = []
        size = len(tokens)
        if not self.case_sensitive:
            tmp_tokens = map(lambda s: s.lower(), tokens)
        else:
            tmp_tokens = tokens
        ix = 0
        while ix < size:
            if debug:
                print "ix", ix
            best, best_key = None, None
            tmp_ix = ix
            max_ix = ix
            current = ""
            d = self.nested
            while tmp_ix < size and tmp_tokens[tmp_ix] in d:
                current += tmp_tokens[tmp_ix] + " "
                key = current.strip()
                if key in self.mapper:
                    if debug:
                        if best is not None:
                            print(ix, tmp_ix, "new best:", key, "=>", self.mapper[key])
                        else:
                            print(ix, tmp_ix, "best:", key, "=>", self.mapper[key])
                    best = self.mapper[key]
                    best_key = key
                    max_ix = tmp_ix
                d = d[tmp_tokens[tmp_ix]]
                tmp_ix += 1
            if not best:
                #retain original casing
                mapped.append(tokens[ix])
            else:
                ix = max_ix
                #yields a set
                for item in sorted(best):
                    mapped.append(item)
            ix += 1
        return mapped

    def __repr__(self):
        return "Synonym Mapper: %i synonyms mapped" % len(self.mapper)

def build_synonym_filter(files, case_sensitive=False):
    # recursively define a defaultdict generator
    mapper = defaultdict(set)
    def dd():
        return defaultdict(dd)
    nested_map = defaultdict(dd)
    file_locn = dict()
    if type(files) == str:
        files = [files]
    for f in files:
        with open(f, "r+") as fin:
            for line in fin:
                line = line.strip()
                if len(line) > 0 and not line[0] == "#":
                    if "=>" in line:
                        left, right = line.split("=>")
                        right = set(right.split(","))
                        left_parts = left.split(",")
                    else:
                        left_parts = line.split(",")
                        right = set(left_parts)

                    for syn in left_parts:
                        for rhs in right:
                            mapper[syn].add(rhs)
                        file_locn[syn] = f

                        tokens = syn.split(" ")
                        prev = tokens[0]
                        d = nested_map[prev]
                        for token in tokens[1:]:
                            d = d[token]
                            prev = token
    return SynonymMapper(mapper, nested_map, case_sensitive)

#String processing
def white_space_tokenize(s):
    return s.split(" ")

__punct__ = set(".?!,;:")
def remove_punct_at_end(s):
    while len(s) > 1 and s[-1] in __punct__:
        s = s[:-1]
    return s

#Token Filters
def fact_len_filter(max_len):
    def len_filter(tokens):
        return filter(lambda s: len(s) >= max_len, tokens)
    return len_filter

remove_empty_tokens_filter = fact_len_filter(1)

def lower_case_filter(tokens):
    if type(tokens) == str:
        return tokens.lower()
    return map(lambda t: t.lower(), tokens)

__punct__ = set(".?!,;:")

def remove_punct_at_end_filter(tokens):
    return map(remove_punct_at_end, tokens)

def fact_is_synonym_filter(syn_mapper):
    def is_synonym_filter(tokens):
        return filter(syn_mapper.is_synonym, tokens)
    return is_synonym_filter


def fact_case_sensitive_stop_word_filter(stop_words_file):
    stop_words = load_stop_words(stop_words_file)

    def cs_stop_filter(tokens):
        return [tok for tok in tokens if tok not in stop_words]
    return cs_stop_filter

def fact_stop_word_filter(stop_words_file):
    stop_words = load_stop_words(stop_words_file)

    def stp_flter(tokens):
        return [tok for tok in tokens if tok.lower() not in stop_words]
    return stp_flter

def analyze(s, filters):
    temp = s
    for f in filters:
        temp = f(temp)
    return temp

def debug_analyze(s, filters):
    temp = s
    pad = 20
    print "START".ljust(pad), temp
    for f in filters:
        temp = f(temp)
        if type(temp) == list:
            s_temp = "|".join(map(str,temp))
        else:
            s_temp = str(temp)
        print f.func_name.ljust(pad), s_temp
    return temp
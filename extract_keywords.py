import time, hashlib, re
from collections import defaultdict
from Utils.string_utils import collapse_spaces
from Utils.file_utils import find_files, load_stop_words

def compute_ngrams(tokens, max_len = None, min_len = 1):
    """
    tokens  :   iterable of string
                    a single sentence of tokens. Assumes start and stop tokens omitted
    max_len :   int
                    maximum ngram length
    min_len :   int
                    minimum ngram length

    """
    if max_len == None:
        max_len = len(tokens)

    if min_len > max_len:
        raise Exception("min_len cannot be more than max_len")

    ngrams = set()
    # unigrams
    for ngram_size in range(min_len, max_len + 1):
        for start in range(0, len(tokens) - ngram_size + 1):
            end = start + ngram_size -1
            words = []
            for i in range(start, end + 1):
                words.append(tokens[i])
            ngrams.add(tuple(words)) # make a tuple so hashable
    return ngrams

# is a valid token
__bad_chars__ = "<>{}[]~@"
__punct__ = set(".?!,;:")
def is_valid_term(term):
    # remove single char entries and only numeric
    if len(term) == 0:
        return False
    if len(term) == 1:
        #else misses c and r
        if term.isalpha():
            return True
        return False
    # no html or js terms
    for c in __bad_chars__:
        if c in term:
            return False
    if term[-1] in __punct__:
        return False
    if "function(" in term:
        return False
    if "!" in term or "?" in term:
        return False
    digit_chars = 0.0
    for c in term:
        if c.isdigit() or not c.isalnum():
            digit_chars += 1.0
    # 60% digits?
    if (digit_chars / len(term)) >= 0.75:
        return False
    return True

re1 = re.compile("[;:\'\"\*/\),\(\-\|\s]+")

# we may want to keep some non-alpha characters, such as # in C# and + in C++, etc.
def remove_punct(s):
    s = s.replace("'s"," ")
    return collapse_spaces(re1.sub(" ",s).strip())

def hash_string(s):
    hash_object = hashlib.md5(b'%s' % s)
    return str(hash_object.hexdigest())

def find_sub_phrases_to_remove(tpl_phrase, valid_phrases, doc_freq, to_rem):
    if len(tpl_phrase) <= 1:
        return
    phrase_df = doc_freq[tpl_phrase]
    ngrams = compute_ngrams(tpl_phrase, len(tpl_phrase)-1, 1)
    for tpl_ngram in ngrams:
        if tpl_ngram in valid_phrases and tpl_ngram not in to_rem:
            sub_phr_df = doc_freq[tpl_ngram]
            # if sub_phrase_df is close to the same frequency
            if phrase_df >= (0.9 * sub_phr_df):
                to_rem.add(tpl_ngram)
                #to_rem_dbg.add((tpl_phrase, tpl_ngram, phrase_df, sub_phr_df))
                find_sub_phrases_to_remove(tpl_ngram, valid_phrases, doc_freq, to_rem)

""" Extract Phrases """
import sys
from Config.extract_keywords_config import ExtractKeywordsConfig

if len(sys.argv) != 2:
    raise Exception("Incorrect number of arguments passed - one expected, the config file name")

#sys.argv[0] is this script file, sys.argv[1] should be the config file
config = ExtractKeywordsConfig(sys.argv[1])
script_start = time.time()

if config.stop_words_file:
    stop_words = load_stop_words(config.stop_words_file)
    print("%i stop words loaded" % len(stop_words))
else:
    stop_words = set()

""" Load Documents """
start = time.time()
files = find_files(config.processed_documents_folder, config.file_mask, True)
print("%s files found in %s" % (len(files), config.processed_documents_folder))
documents = []
for i, fname in enumerate(files):
    with open(fname) as f:
        contents = f.read()
        documents.append(contents.split("\n"))
end = time.time()
print("Loading %i documents took %s seconds" % (len(files), str(end - start)))

""" Extract Common Terms and Phrases """
start = time.time()
#Or use a counter here.
doc_freq = defaultdict(int)

# remove short docs
tokenized_docs = []
sent_id = 0
sent_ids = set()
lens = []
hashed = set()

""" Find single word keywords """
for doc in documents:
    un_tokens = set()
    tok_sents = []
    for sent in doc:
        cl_sent = remove_punct(sent.lower())
        hash_sent = hash_string(cl_sent)
        # remove dupe sentences (not - will hurt df accuracy a little)
        if hash_sent in hashed:
            continue
        hashed.add(hash_sent)

        tokens = tuple(cl_sent.split(" "))
        lens.append(len(tokens))
        sent_id += 1
        tok_sents.append((sent_id, tokens))
        sent_ids.add(sent_id)

        # create inverted index and unique tokens (for doc freq calc)
        proc_tokens = set()
        for tok in tokens:
            if not tok in proc_tokens:
                proc_tokens.add(tok)
                if not tok in un_tokens:
                    un_tokens.add(tok)
                    doc_freq[tok] += 1

    if len(tok_sents) > 0:
        tokenized_docs.append(tok_sents)

end = time.time()
print("Extracting Keywords from %i documents took %i secs" % (len(tokenized_docs), end-start))

# Get really frequent items for removal
num_docs = float(len(tokenized_docs))
above_threshold = [k for k,v in doc_freq.items() if v >= config.min_document_frequency]

# remove really frequent terms (in 50% or more of documents)
too_freq = set([k for k in above_threshold if (doc_freq[k]/num_docs) >= config.max_proportion_documents])

freq_terms = [k for k in above_threshold
              if  k not in stop_words and
                  k not in too_freq and
                  is_valid_term(k)]
print("%s frequent terms identified for building phrases" % len(freq_terms))

""" Find Phrases """
import time

start = time.time()

# Find all phrases up to length MAX_PHRASE_LEN at or above the defined MIN_DOC_FREQ above
phrase_doc_freq = defaultdict(int)
for term in freq_terms:
    phrase_doc_freq[tuple([term])] = doc_freq[term]

# data structure is a list of list (document) of pairs - sentences: (int, list  (of tokens))
# each item is a doc, a list of sents. each sent is a list of valid remaining phrases
# seed with one valid phrase per sent

#working_docs = [map(lambda sent: [sent], d) for d in tokenized_docs]
working_docs = [map(lambda (sid, sent): (sid, [sent]), d) for d in tokenized_docs]
working_freq_terms = set(freq_terms)

# sentences with one or more phrases that are frequent enough (under the apriori algorithm closure priniciple)
working_sent_ids = set(sent_ids)
# don't bother whitling this down further at the start, almost all sentences have at least on freq term in them

for phrase_len in range(2, config.max_phrase_length + 1):
    phrase_start = time.time()
    print "phrase_len", phrase_len
    print len(working_docs), "docs", len(working_freq_terms), "terms", len(working_sent_ids), "sentences"
    # for current phrase_len
    current_phrase_doc_freq = defaultdict(int)

    # used to look up sentence ids by phrase
    phrase2sentids = defaultdict(set)

    new_work_docs = []
    for doc in working_docs:
        new_work_sents = []
        unique_potential_phrases = set()
        for sent_id, phrases in doc:
            if sent_id not in working_sent_ids:
                continue

            new_work_phrases = []
            for phrase in phrases:
                current_phrase = []
                for term in phrase:
                    if term in working_freq_terms:
                        current_phrase.append(term)
                    else:
                        if len(current_phrase) >= phrase_len:
                            new_work_phrases.append(current_phrase)
                        current_phrase = []

                if len(current_phrase) >= phrase_len:
                    new_work_phrases.append(current_phrase)

            if len(new_work_phrases) > 0:
                for phrase in new_work_phrases:
                    ngrams = compute_ngrams(phrase, phrase_len, phrase_len)
                    for tpl_ngram in ngrams:
                        unique_potential_phrases.add(tpl_ngram)
                        phrase2sentids[tpl_ngram].add(sent_id)

                new_work_sents.append((sent_id, new_work_phrases))

        # end for sent in doc
        # for doc freq, need to compute unique phrases in document
        for unique_tpl_phrase in unique_potential_phrases:
            current_phrase_doc_freq[unique_tpl_phrase] +=1

        if len(new_work_sents) > 0:
            new_work_docs.append(new_work_sents)

    new_working_freq_terms = set()
    new_working_sent_ids = set()
    for tuple_phrase, freq in current_phrase_doc_freq.items():
        if freq < config.min_document_frequency:
            continue
        phrase_doc_freq[tuple_phrase] = freq
        new_working_sent_ids.update(phrase2sentids[tuple_phrase])
        for tok in tuple_phrase:
            new_working_freq_terms.add(tok)

    if len(new_working_freq_terms) <= 1 or len(new_work_docs) == 0 or len(new_working_sent_ids) == 0:
        break
    working_docs = new_work_docs
    working_freq_terms = new_working_freq_terms
    working_sent_ids = new_working_sent_ids
    phrase_end = time.time()
    print("\t%iphrases found" % len(phrase_doc_freq))
    print("\ttook %i seconds" % (phrase_end - phrase_start))

print ""
end = time.time()
print("\t%i phrases found" % len(phrase_doc_freq))
print("\ttook %i seconds" % (end - start))

""" Remove Sub-Phrases """
# there are a lot of short phrases that always or nearly always have the same DF as longer phrases that they constitute

# don't process unigrams
valid_phrases = set(phrase_doc_freq.keys())
phrases = filter(lambda k: len(k) > 1, phrase_doc_freq.keys())
to_remove = set()

for tpl_key in sorted(phrases, key = lambda k: -len(k)):
    if tpl_key not in to_remove:
        phrase_df = phrase_doc_freq[tpl_key]
        # find all shorter sub-phrases
        find_sub_phrases_to_remove(tpl_key, valid_phrases, phrase_doc_freq, to_remove)
print("%i sub-phrases found for removal" % len(to_remove))

#Dump phrases to file
cnt = 0
with open(config.keywords_file, "w+") as f:
    for tpl in sorted(phrase_doc_freq.keys()):
        # phrases only
        if tpl not in to_remove:
            cnt+=1
            joined = " ".join(tpl)
            f.write(joined + "\n")

print("%i phrases written to the file: %s" % (cnt, config.keywords_file))
full_end = time.time()
print("Whole process took %s seconds" % str(full_end - script_start))
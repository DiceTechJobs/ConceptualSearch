import time
from gensim.models.word2vec import Word2Vec
from Utils.string_utils import clean_str
from Utils.file_utils import find_files, load_stop_words
from Config.generate_topn_synonyms_config import GenerateTopNSynonymsConfig
import sys

def map_keyword(kw):
    return kw.replace(" ", "_")

def write_most_similar_synonyms(topn, key_words, model, payload_file, synonym_file):
    key_words = set(key_words)
    missing = set()
    no_sim = set()
    processed_syns = set()
    with open(payload_file, "w+") as pyld_f:
        for word in key_words:
            if not word in model.vocab:
                #print("Word: '%s' not found in model vocabulary." % word)
                missing.add(word)
                continue

            top_matches = model.most_similar(positive=word, topn=topn*10)
            valid = []
            for t,sim in top_matches:
                if sim < 0.01:
                    break
                if t in key_words:
                    valid.append((t,sim))
                    if len(valid) >= topn:
                        break

            if len(valid) > 0:
                processed_syns.add(word)
                pyld_f.write("%s=>" % word)
                for key, val in valid:
                    processed_syns.add(key)
                    kw = map_keyword(key)
                    pyld_f.write("%s|%f " %(kw,val))
                pyld_f.write("\n")
            else:
                no_sim.add(word)
                #print("No matching similar terms in word2vec model for term: %s" % word)
    with open(synonym_file, "w+") as f:
        for syn in sorted(processed_syns):
            f.write("%s=>%s\n" % (syn, map_keyword(syn)))
    #Returned for analysis - do something with this if you need to investigate
    return missing, no_sim, processed_syns

""" Generate Synonym Files """
if len(sys.argv) != 2:
    raise Exception("Incorrect number of arguments passed - one expected, the config file name")

config = GenerateTopNSynonymsConfig(sys.argv[1])

start = time.time()
model = Word2Vec.load(config.model_file)
print("Word2Vec model loaded")

keywords = set()
for file in config.keywords_files:
    keywords.update(load_stop_words(file))
print("%i keywords loaded" % (len(keywords)))

missing, no_sim, processed_syns = write_most_similar_synonyms(config.top_n, keywords, model, config.payload_synonyms_file, config.synonyms_file)
print "%s synonyms processed" % (len(processed_syns))

end = time.time()
print "Took %s seconds" % (end - start)
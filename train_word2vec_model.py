import time
from gensim.models.word2vec import Word2Vec
from Utils.string_utils import clean_str
from Utils.file_utils import find_files
from analysis_pipeline import analyze, debug_analyze
from analysis_pipeline import build_synonym_filter, fact_case_sensitive_stop_word_filter, fact_stop_word_filter
from analysis_pipeline import fact_is_synonym_filter, white_space_tokenize, remove_punct_at_end_filter, lower_case_filter, remove_empty_tokens_filter
from Config.train_word2vec_model_config import TrainWord2VecModelConfig
import sys

""" TRAIN Word 2 Vec Model"""

if len(sys.argv) != 2:
    raise Exception("Incorrect number of arguments passed - one expected, the config file name")

config = TrainWord2VecModelConfig(sys.argv[1])

""" Load analysis chain """
syn_mapper = build_synonym_filter(config.keywords_files, config.case_sensitive)

if config.case_sensitive:
    stop_filter = fact_case_sensitive_stop_word_filter(config.stop_words_file)
else:
    stop_filter = fact_stop_word_filter(config.stop_words_file)

# Simon Hughes: This is quite inefficient, as each function is applied in turn
# resulting in multiple passes over the token stream. While not currently a
# big performance bottleneck, could be much faster.
#  - TODO: use functional composition to speed up
is_a_synonym_filter = fact_is_synonym_filter(syn_mapper)
analysis_chain = [clean_str,
                  white_space_tokenize,
                  remove_punct_at_end_filter,
                  lower_case_filter,
                  stop_filter,
                  syn_mapper.map_synonyms,
                  remove_empty_tokens_filter]
                  # is_a_synonym_filter] - Un-comment to just train on keywords.

#Test
#rslt = debug_analyze("$150k as400 Sr.\ Java/j2ee and the C#.! developer. FIT \"HOT\" dev. -IBM's business, sql server management", analysis_chain)

""" Load Documents """
start = time.time()

sentences = []
files = find_files(config.processed_documents_folder, config.file_mask, True)
print("%s files found in %s" % (len(files), config.processed_documents_folder))

documents = []
for i, fname in enumerate(files):
    with open(fname) as f:
        contents = f.read()
        sentences.extend(contents.split("\n"))
end = time.time()
print("Loading %i sentences took %s seconds" % (len(sentences), str(end - start)))

""" Analyze - clean, tokenize, extract phrases """
print("%i sentences to process" % len(sentences))

tokenized = []
print("Tokenizing sentences")
for i, sent in enumerate(sentences):
    tokens = analyze(sent, analysis_chain)
    if len(tokens) >= config.min_sentence_length_words:
        tokenized.append(tokens)
    if i % 100000 == 0:
        print(i)

""" Train Model """

start = time.time()

print("Training Model. This could take a while (10-60 mins for moderate collections). Get a coffee")
model = Word2Vec(tokenized, iter=config.training_iterations, size=config.vector_size, window=config.window_size, min_count=config.min_word_count, workers=config.workers, sample=1e-5, hs=0, negative=20)
model.save(config.model_file)
end = time.time()
print "Took %s seconds" % (end - start)
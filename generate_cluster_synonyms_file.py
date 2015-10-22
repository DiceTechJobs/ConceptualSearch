from sklearn.cluster import KMeans

from collections import defaultdict
from gensim.models.word2vec import Word2Vec
from Utils.file_utils import  load_stop_words
from Config.generate_cluster_synonyms_config import GenerateClusterSynonymsConfig
import numpy as np
import time
import sys

def get_vector(item, model):
    vocab = model.vocab[item]
    vector = model.syn0[vocab.index]
    return vector

def get_norm_vector(item, model):
    if item not in model.vocab:
        return None
    # for deserialized models, the norm vectors are not stored
    vec = get_vector(item, model)
    norm = np.linalg.norm(vec)
    if norm != 0:
        return vec / norm
    return vec

def map_keyword(kw):
    return kw.replace(" ", "_")

def extract_clusters(ids, id2kwd):
    clusters = defaultdict(set)
    for kw_id, label in enumerate(ids):
        kw = id2kwd[kw_id]
        clusters[label].add(kw)
    return clusters

# expand at query time
# use with tfidf (on cluster labels) at index time by just mapping to cluster label
def write_most_similar_clusters(topn, kwd2cluster_sims, synonym_qry_fname, synonyn_index_fname):
    kwords = sorted(kwd2cluster_sims.keys())
    cluster_label = lambda lbl: "cluster_" + str(lbl)

    with open(synonym_qry_fname, "w+") as qry_f:
        for kword in kwords:
            cl_sims = kwd2cluster_sims[kword]
            # unlike the other methods, we DO want to include the first cluster here
            # as it's a cluster rather than the top 10 or top 30 keyword method
            top_clusters = cl_sims[:topn]
            if len(top_clusters) > 0:
                qry_f.write("%s=>" % kword)
                for lbl, sim in top_clusters:
                    qry_f.write("%s|%f " %(cluster_label(lbl),sim))
                qry_f.write("\n")

    with open(synonyn_index_fname, "w+") as f:
        for kword in kwords:
            # get top cluster label
            lbl, sim = kwd2cluster_sims[kword][0]
            f.write("%s=>%s\n" % (kword, cluster_label(lbl)))


""" Extract Clustered Synonyms """
if len(sys.argv) != 2:
    raise Exception("Incorrect number of arguments passed - one expected, the config file name")

config = GenerateClusterSynonymsConfig(sys.argv[1])

script_start = time.time()
model = Word2Vec.load(config.model_file)
print("Word2Vec model loaded")

keywords = set()
for file in config.keywords_files:
    keywords.update(load_stop_words(file))
print("%i keywords loaded" % (len(keywords)))

id2kwd = dict()
kwd2id = dict()
vectors = []
for term in keywords:
    id2kwd[len(vectors)] = term
    kwd2id[term] = len(vectors)
    vec = get_norm_vector(term, model)
    if vec is not None:
        vectors.append(vec)

start = time.time()

# don't parallelize (n_jobs = -1), doesn't seem to work
print("Clustering vectors into %i clusters" % config.num_clusters)
km_clusterer = KMeans(n_clusters=config.num_clusters, n_jobs=1, verbose=1, n_init=5)
ids = km_clusterer.fit_predict(vectors)

end = time.time()
print("Creating %i clusters took %i seconds" % (config.num_clusters, end - start))

lbl2cluster = extract_clusters(ids, id2kwd)

with open(config.synonyms_file, "w+") as f:
    for lbl, words in lbl2cluster.items():
        f.write(str(lbl) + "|")
        line = ",".join(sorted(words))
        f.write(line + "\n")
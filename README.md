# Conceptual Search

Python code for training the Thomas Mikolov's Word2Vec model on a set of documents. The output of this process can then be embedded in solr using synonym files, optionally combined with some solr plugings to provide conceptual search functionality within the search engine. The output could also be used within other search engines, provided they support synonym files. Conceptual search is also known as semantic search, and learns to match across concepts in a domain rather than keywords to improve recall.

The scripts include code to pre-process and tokenize documents, extract common terms and phrases based on document frequency, train a word2vec model using the gensim implementation, and cluster the resulting word vectors using sci-kit learn's clustering libraries. The python scripts output a number of solr synonym files which can be used to enable conceptual search functionality within solr when combined with some custom dice solr plugins.

See https://github.com/DiceTechJobs/SolrPlugins for solr plugins to utilize the learned vectors and synonym files within an Apache Solr search engine

See https://github.com/DiceTechJobs/SolrConfigExamples for example solr configuration entries for configuring conceptual search within solr, including setting up the plugins.

Currently the scripts are in the form of Jupyter python notebooks, to be run in order (1,2,3 and 4). 

**UPDATE** I have added 3 of the command line scripts. These will train the model. I need to add the final scripts to create the output files (or using Jupyter notebooks 4.*). The settings folder contains example config files for each script, with documentation describing eaching setting. To call the command line scripts, pass in the related config file as the solr paramater, e.g.

```bash
python pre_process_documents.py ./Settings/pre_process_documents.cfg
```


## Required Python libraries:

* nltk (for sentence tokenizer in pre-processing file)
* beautiful-soup (for html parsing in pre-processing script)
* numpy
* gensim (for Word2Vec implementation)
* scikit-learn (only needed for clustering)
* jupyter (to use the notebooks - jupyter is the new name for ipython)

Built using python 2.7.10. Untested with python 3

## Word2Vec
The Word2Vec implementation is that of the excellent gensim package. Contains an exellent implementation of LSA, LDA, Word2Vec and some other machine learning algorithms.

https://radimrehurek.com/gensim/models/word2vec.html

This is an excellent package for topic modelling, and learning semantic representations of documents and words.

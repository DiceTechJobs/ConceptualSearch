# ConceptualSearch
Python code for training the Thomas Mikolov's Word2Vec model on a set of documents. Includes code to pre-process and tokenize documents, extract common terms and phrases by document frequency, train a word2vec model using the gensim implementation, and cluster the resulting word vectors using sci-kit learn's clustering libraries. The python scripts output a number of solr synonym files which can be used to enable conceptual search functionality within solr when combined with some custom dice solr plugins.

See https://github.com/DiceTechJobs/SolrPlugins for solr plugins to utilize the learned vectors and synonym files within an Apache Solr search engine

See https://github.com/DiceTechJobs/SolrConfigExamples for example solr configuration entries for configuring conceptual search within solr, including setting up the plugins.

Currently the scripts are in the form of Jupyter python notebooks, to be run in order (1,2,3 and 4). I will shortly convert these into command line scripts with accompanying documentation.

## Required Python libraries:

* nltk (for sentence tokenizer in pre-processing file)
* beautiful-soup (for html parsing in pre-processing script)
* numpy
* gensim (for Word2Vec implementation)
* scikit-learn (only needed for clustering)

Built using python 2.7.10. Untested with python 3

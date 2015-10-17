# Conceptual Search

Dice Tech Job - Dice.com's repository for building a conceptual search model. This repository contains Python code for training Thomas Mikolov's Word2Vec model on a set of documents. The output of this process can then be embedded in solr (or some other search engine) using synonym files combined with some solr plug-ins to provide conceptual search functionality within the search engine. The output could also be used within other search engines, provided they support synonym files. Conceptual search is also known as semantic search, and learns to match across concepts in a domain rather than keywords to improve recall.

The scripts include code to pre-process and tokenize documents, extract common terms and phrases based on document frequency, train a word2vec model using the gensim implementation, and cluster the resulting word vectors using sci-kit learn's clustering libraries. The python scripts output a number of solr synonym files which can be used to enable conceptual search functionality within solr when combined with some custom dice solr plugins.

See https://github.com/DiceTechJobs/SolrPlugins for solr plugins to utilize the learned vectors and synonym files within an Apache Solr search engine

See https://github.com/DiceTechJobs/SolrConfigExamples for example solr configuration entries for configuring conceptual search within solr, including setting up the plugins.

Currently the scripts are in the form of Jupyter python notebooks, to be run in order (1,2,3 and any of the 4's). 

**UPDATE** I have added 3 of the 6 necessary command-line scripts if you want to avoid using Jupyer. These will pre-process the documents, and train the Word2Vec model. I need to add the final scripts to create the output files (or you can use the Jupyter notebooks 4.1, 4.2 and 4.3). The ./Settings folder contains example config files for each script, with a desription of each setting in the comments (hash prefixed). To call the command-line scripts, pass in the related config file as the only paramater, e.g.

```bash
python pre_process_documents.py ./Settings/pre_process_documents.cfg
```
The command line scripts should be run in order:

1. pre_process_documents.py - this is needed to strip-out some punctuation characters (comma's, hyphens etc), parse html if needed, and separate out the sentences in the document. **If** you wish to skip this step and move to 2 or 3, provide a set of files to steps 2 and 3 with any punctuation you want removing stripped out, and with every new sentence on a separate line.

2. extract_keywords.py - (optional) If you don't have a good and extensive set of keyphrases from your domain (e.g. your top 5,000 seach keywords and phrases, phrases being the important part) or you want to increase coverage beyond this list, run this script to extract all keywords and phrases above a specified document frequency threshold.

3. train_word2vec_model.py - Trains and saves the Word2Vec model on the pre-processed documents from 1. Uses a set of keywords and phrases, such as those output from 2. Please take note of any runtime warnings. **Please note** - This model is very fast, but requires a C compiler to be available and pre-installed to make use of the C version under the covers, otherwise the much slower python implementation is used.

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

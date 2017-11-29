# DiceTechJobs - Conceptual Search

Dice Tech Jobs - Dice.com's repository for building a 'Conceptual Search Engine', by Simon Hughes ( Dice Data Scientist ). This repository contains Python code for training Thomas Mikolov's Word2Vec model on a set of documents. The output of this process can then be embedded in solr (or some other search engine) using synonym files combined with some solr plug-ins to provide conceptual search functionality within the search engine. The output could also be used within other search engines, provided they support synonym files. Conceptual search is also known as semantic search, and learns to match across concepts in a domain rather than keywords to improve recall.

## Links
* [Slides from the talk](http://www.slideshare.net/lucidworks/implementing-conceptual-search-in-solr-using-lsa-and-word2vec-presented-by-simon-hughes-dicecom)
* [Video of the Talk](https://www.youtube.com/watch?v=WYOkb1BQG2E)
* [Recap of Lucene Revolution 2015 by Open Source Connections](http://opensourceconnections.com/blog/2015/10/29/lucene-revolution-2015-austin/)
* [Related: Semantic Search with LSA - Open Source Connections](http://opensourceconnections.com/blog/2016/03/29/semantic-search-with-latent-semantic-analysis/)
* [Lucidworks: Focusing on Search Quality in Lucene Revolution 2015](https://lucidworks.com/blog/2015/10/19/focusing-on-search-quality-at-lucenesolr-revolution-2015/)

## Description
The scripts include code to pre-process and tokenize documents, extract common terms and phrases based on document frequency, train a word2vec model using the gensim implementation, and cluster the resulting word vectors using sci-kit learn's clustering libraries. The python scripts output a number of solr synonym files which can be used to enable conceptual search functionality within solr when combined with some custom dice solr plugins.

See https://github.com/DiceTechJobs/SolrPlugins for solr plugins to utilize the learned vectors and synonym files within an Apache Solr search engine

See https://github.com/DiceTechJobs/SolrConfigExamples for example solr configuration entries for configuring conceptual search within solr, including setting up the plugins.

The scripts are in the form of Jupyter python notebooks, to be run in order (1,2,3 and any of the 4's), and as separate command line scripts (see below) if you don't want to use Jupyter. **The python scripts are cleaner, and share common config files with all required settings, and are designed to be run from the shell, so these are probably easier to start with**. These notebooks and scripts will pre-process the documents, and train the Word2Vec model. The ./Settings folder contains example config files for each script, with a description of each setting in the comments. To call the command-line scripts, pass in the related config file as the only paramater, e.g.

```bash
python pre_process_documents.py ./Settings/pre_process_documents.cfg
```
The command line scripts should be run in order:

1. pre_process_documents.py - this is needed to strip-out some punctuation characters (comma's, hyphens etc), parse html if needed, and separate out the sentences in the document. **If** you wish to skip this step and move to 2 or 3, provide a set of files to steps 2 and 3 with any punctuation you want removing stripped out, and with every new sentence on a separate line.

2. extract_keywords.py - (optional) If you don't have a good and extensive set of keyphrases from your domain (e.g. your top 5,000 seach keywords and phrases, phrases being the important part) or you want to increase coverage beyond this list, run this script to extract all keywords and phrases above a specified document frequency threshold.

3. train_word2vec_model.py - Trains and saves the Word2Vec model on the pre-processed documents from 1. Uses a set of keywords and phrases, such as those output from 2. **Please note** - This model is very fast, but requires a C compiler to be available and pre-installed to make use of the C version under the covers, otherwise the much slower python implementation is used. If this is unavailable, you will get a run-time warning when the model is first trained.

4. This step contains multiple files depending on the desired solution (see my talk):
  1. Vector output - COMING SOON! See Jupyter Notebook 4.a
  2. generate_topn_synonyms_file.py - Generates top n synonyms for each target keyword or phrase. This generates 2 files, a file with payloads, and a file without. The simplest use case is to use the file without payloads. Better performance can be gained using the payloads file to weight the synonyms by similarity. This can be done at query time using the queryboost parser. Note that to do this you need to tokenize on commas and whitespace at query time as we replace whitespace with commas to get around the multi-word synonym issue. Alternatively (and recommended) use synonym expansion at index time, along with the PayloadEdismax query parser, the PayloadAwareDefaultSimilarity class (use as default similarity or use schema similarity to configure per field), and ensure the fieldType for these fields contains the term 'payload' or 'vector'.
  3. generate_cluster_synonyms_file.py - Generates k clusters from the word vectors generated in the previous steps. These can be embedded directly in solr via a synonym file - no special plugins needed. I'd recommend generating a number of different clusters of synonyms of varying sizes, and configure these as separate fields with higher field weights applied to the small clusters (i.e. generated with a larger k value).

## Required Python libraries:

* nltk (for sentence tokenizer in pre-processing file)
* beautiful-soup (for html parsing in pre-processing script)
* numpy
* gensim (for Word2Vec implementation)
* scikit-learn (only needed for clustering)
* jupyter (to use the notebooks - jupyter is the new name for ipython)

Built using python 2.7.10. Untested with python 3

## Word2Vec
The Word2Vec implementation is that of the excellent gensim package. Contains fast implementations of LSA, LDA, Word2Vec and some other machine learning algorithms.

https://radimrehurek.com/gensim/models/word2vec.html

This is a great package for topic modelling, and learning semantic representations of documents and words.

## Using Pre-Trained Word Vectors
Google released a set of pre-trained word vectors, trained on a 100 billion words of the google news corpus. For those of you that aren't focused in a specialized domain but on a very broad set of documents, such as companies building a news search engine (like Reuters, Bloomberg, Governmental agencies, etc) you can just use this pre-trained model instead. Then you can skip the first 3 steps, and go directly to using one of the step 4 scripts above that take a pre-trained model and compute output synonym files, and that's all you should need. This post describes where to get the pre-trained vectors: https://groups.google.com/forum/#!topic/gensim/_XLEbmoqVCg. You can then use gensim's Word2Vec's model.load functionality:
```python
model = Word2Vec.load(MODEL_FILE)
```
## A Note on Synonym File Sizes
If you are using Solr cloud, Zookeeper does not like any config files to be over 1M in size. So if your resulting synonym files are larger than this, you will either have to either 1) change the default zookeeper settings, 2) split the synonym file into mutliple files and apply synonym filters in sequence, or 3) load synonyms from a database using a plugin (e.g. https://github.com/shopping24/solr-jdbc-synonyms)

## Stanford's Glove Vectors
Stanford's NLP boffins developed a competing word vector learning algorithm to Word2Vec with similar accuracy. If you want to experiment with that, this python package will allow you to do so:
https://github.com/hans/glove.py
I haven't however tried that so I can't vouch for it at this time.

## Input File Format
The intial scripts expect a folder containing raw \*.txt or html files. If you have html content, there is logic inside the scripts to parse the html, but beautiful soup can be a bit flaky, so you may be better pre-parsing them first before pushing them through the pipeline. Note that there is no special file format, which seems to be the issue most people have when trying to run this script. If it's erroring out loading the files, I'd suggest using the python script not the notebook and cracking open the debugger to see what's happening. Also, make sure you set the config.file_mask to match the files you want to load, in https://github.com/DiceTechJobs/ConceptualSearch/blob/master/Settings/pre_process_documents.cfg. This defaults to \.*.txt (it's a regex not a file blob), so you will need to change this if you files are not .txt files.

## Troubleshooting \ Errors
Please post any questions, bugs or feature requests to the issues list, and include an @mention - @simonhughes22 so I'll get a timely email with your questions. I have had a few people email me directly with questions about this repo. While I don't mind responding to emails, **Please instead submit a GitHub issue and @mention me.** That way, everyone else can see the question and my response for future reference.

## Other Tools
Please check out our Solr plugins:
- https://github.com/DiceTechJobs/SolrPlugins
- https://github.com/DiceTechJobs/RelevancyFeedback

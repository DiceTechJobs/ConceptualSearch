import os, re, time
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from Utils.string_utils import clean_str, strip_non_ascii
from Utils.file_utils import find_files, delete_files
import ntpath

__REPL__ = ".\n"

# Make common html tags line breaks
def pre_process_text(txt):
    txt = txt.replace("</li><li>", __REPL__).replace("<li>", __REPL__).replace("</li>", __REPL__)
    txt = txt.replace("<br>", __REPL__)
    txt = txt.replace("<br/>", __REPL__)
    txt = txt.replace("<br />", __REPL__)
    txt = txt.replace("<p>",  __REPL__)
    txt = txt.replace("<p/>",  __REPL__)
    txt = txt.replace("<p />",  __REPL__)
    txt = txt.replace("</p>", __REPL__)
    txt = txt.replace(". .",  __REPL__)
    txt = txt.replace("&nbsp;", " ")
    while ".." in txt:
        txt = txt.replace("..", ". ")
    while "  " in txt:
        txt = txt.replace("  ", " ")
    return txt

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', strip_non_ascii(element)):
        return False
    return True

def get_text(html):
    bs = BeautifulSoup(html)
    texts = bs.findAll(text=True)
    visible_texts = filter(visible, texts)
    return __REPL__.join(visible_texts)

def parse_html(html):
    txt = get_text(pre_process_text(html))
    return txt

def split_into_sentences(txt):
    txt = strip_non_ascii(txt)
    sents = map(clean_str,sent_tokenize(txt))
    return filter(lambda s: len(s.strip()) > 5, sents)

ntpath.basename("a/b/c")
def get_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

""" Process Files """
import sys
from Config.pre_process_config import PreProcessConfig

if len(sys.argv) != 2:
    raise Exception("Incorrect number of arguments passed - one expected, the config file name")

#sys.argv[0] is this script file, sys.argv[1] should be the config file
config = PreProcessConfig(sys.argv[1])

start = time.time()

if config.empty_processed_documents_folder:
    delete_files(config.processed_documents_folder, config.file_mask)

files = find_files(config.documents_folder, config.file_mask, True)
for i, fpath in enumerate(files):
    with open(fpath) as f:
        contents = f.read()
        if len(contents) < config.minimum_file_size_chars:
            continue
        if config.parse_html:
            contents = parse_html(contents)
            if len(contents) < config.minimum_file_size_chars:
                continue

        sents = split_into_sentences(contents)
        doc = "\n".join(sents)

        file_name = get_file_name(fpath)
        fout_name = config.processed_documents_folder + "/" + file_name.split(".")[0] + "_proc.txt"
        with open(fout_name, "w+") as fout:
            fout.write(doc)
        if i % 1000 == 0 and i > 0:
            print("%i documents processsed" % i)
end = time.time()
print("Loading and processing documents took %s seconds" % str(end - start))
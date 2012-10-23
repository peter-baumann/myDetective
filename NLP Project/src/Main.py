'''
Created on 27.09.2012

@author: Peter
'''
import operator
print "loading libraries...",
import sys
import nltk
import os
import Data
import string
import sqlite3
import re
from fwords import fwords
import math
from corpusstatistics import corpusstatistics
from nltk.corpus import LazyCorpusLoader
from nltk.corpus.reader import *
from nltk.tag import *
from nltk.collocations import *
print "- done"

def training(init = False):
    if init: initData()
    #change this for loading another training corpus:
    #corpus = LazyCorpusLoader('brown', CategorizedTaggedCorpusReader, 
    #                          r'c[a-z]\d\d', cat_file='cats.txt', 
    #                          tag_mapping_function=simplify_brown_tag)
    
    #change this for using a different test method.
    test_method_bi  = nltk.collocations.BigramAssocMeasures().pmi
    test_method_tri = nltk.collocations.TrigramAssocMeasures().pmi
    #corpus_stats = corpusstatistics(corpus)
    #corpus_fword_frequency = corpus_stats.getRelativeFunctionWordFrequency()
    #corpus_bigram_frequency = corpus_stats.getBigramFrequency(test_method)
    
    authors = getAuthors()
    for author in authors:
        for file_ in authors[author]:
            text = Data.Data(file_[1]).text.lower()
            sentences = nltk.sent_tokenize(text)
            words = [x for x in nltk.word_tokenize(text) if x not in string.punctuation and re.search("[0-9]", x) == None and x != "``" and x != "''"]

            #Function word frequency
            fword_frequency = fwordFrequency(words, len(words))
            #store(text_fwords.getCount(), text_fword_frequency, author, file_[0])
            
            #Bigram frequencies
            bigram_frequency = BigramFrequency(words, test_method_bi)
            
            #Trigram frequencies
            trigram_frequency = TrigramFrequency(words, test_method_tri)


    
def testing():
    pass

def testDocument():
    pass    

def main(args):
    training()
    
def fwordFrequency(words, token_count):
    text_fwords = fwords()
    return text_fwords.relativeFrequencyWordArray(words, token_count)

def BigramFrequency(words, test_method):
    return_array = []
    finder = BigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(math.ceil(math.log(len(words) - 1) /3) - 1) #@UndefinedVariable
    scored = finder.score_ngrams(test_method)
    for score in scored:
        if(fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1])):
            return_array.append(score)
    return return_array
    
def TrigramFrequency(words, test_method):    
    return_array = []
    finder = TrigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(math.ceil(math.log(len(words) - 1) /3) - 1) #@UndefinedVariable
    scored = finder.score_ngrams(test_method)
    for score in scored:
        if(fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1]) and fwords.isFunctionWord(score[0][2])):
            return_array.append(score)
    return return_array
    

#just a helper function for finding the students with the most text data
def mostWritten():
    authors = {}
    files = os.listdir("../CORPUS_TXT/")
    for file in files:
        if file[len(file)-3:len(file)] == "txt" and "Freq" not in file:
            size = os.path.getsize("../CORPUS_TXT/" + file)
            author = file[0:len(file)-5]
            if author in authors:
                authors[author][0] = authors[author][0] + size
                authors[author][1] = authors[author][1] + 1
            else:
                authors.update({author:[size, 1]})
                
    authors2 = sorted(authors.items(), key=operator.itemgetter(1), reverse=True)
    print authors2
    authors = sorted(authors.items(), key=lambda (k, v): operator.itemgetter(1)(v), reverse=True)
    print authors

def store(abs_frequencies, rel_frequencies, author_name, filename):
    print "generating training data statistics..."
    #storing results in database
    con = sqlite3.connect("../cache.db") #@UndefinedVariable
    #Add corpus if not already in db
    try:
        with con:
            con.execute("INSERT INTO authors(name) VALUES (?)", [author_name])
    except sqlite3.IntegrityError: #@UndefinedVariable
        pass
    #get author id
    author_id = 0
    for row in con.execute("SELECT rowid FROM authors WHERE name=?", [author_name]):
        author_id = row[0]
    #Add function words if not already in db
    for key in rel_frequencies.iterkeys():
        try:
            with con:
                con.execute("INSERT INTO fwords(name) VALUES (?)", [key])
        except sqlite3.IntegrityError: #@UndefinedVariable
            pass
    #retrieve ids
    ids = {}        
    for key in rel_frequencies.iterkeys():
        for row in con.execute("SELECT rowid FROM fwords WHERE name=?", [key]):
            ids.update({key:row[0]})
    #Add training text if not already in db
    try:
        with con:
            con.execute("INSERT INTO training(filename, author_id) VALUES (?,?)", [filename, author_id])
    except sqlite3.IntegrityError: #@UndefinedVariable
        pass
    #get training id
    for row in con.execute("SELECT rowid FROM training WHERE filename=? AND author_id=?", [filename, author_id]):
        training_id = row[0]      
    #store values in db
    for key in rel_frequencies.iterkeys():
        try:
            with con:
                con.execute("INSERT INTO training_fwords(training_id, fword_id, count, percentage) VALUES (?, ?, ?, ?)", (training_id, ids[key], int(abs_frequencies[key]), str(rel_frequencies[key])))
        except sqlite3.IntegrityError: #@UndefinedVariable
            pass
    
def getAuthors(path = '../training/'):
    """returns a list of authors with corresponding files."""
    authors = {}
    author_listing = os.listdir(path)
    for author in author_listing:
        if os.path.isdir(path + author):
            author_path = os.path.join(path, author) + "/"
            file_listing = os.listdir(author_path)
            file_listing = [[file_, author_path + file_] for file_ in file_listing]
            if len(file_listing) > 0:
                authors.update({author:file_listing})
    return authors
    
def initData():
    #backup of old database if any, for avoiding unintentional data loss
    if os.path.isfile("../cache.db"):
        from time import time
        os.rename("../cache.db", "../cache_bkp" + str(time()) + ".db")
    #creating database
    conn = sqlite3.connect("../cache.db") #@UndefinedVariable
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE corpora (name varchar unique , count integer)")
    cursor.execute("CREATE TABLE fwords (name varchar unique)")
    cursor.execute("CREATE TABLE corpora_fwords (corpus_id integer, fword_id integer, count integer, percentage text)")
    cursor.execute("CREATE TABLE authors (name varchar unique)")
    #TODO : execute once for table creation, store values in db
    cursor.execute("CREATE TABLE training (filename varchar unique, author_id integer, count integer)")
    cursor.execute("CREATE TABLE training_fwords (training_id integer, fword_id integer, count integer, percentage text)")
    conn.commit()
    cursor.close()

if __name__ == '__main__':
    main(sys.exit(main(sys.argv)))    
    
main()
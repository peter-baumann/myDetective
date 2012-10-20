'''
Created on 27.09.2012

@author: Peter
'''
print "loading libraries...",
import sys
import nltk
import os
import Data
import string
import sqlite3
from fwords import fwords
from corpusstatistics import corpusstatistics
from nltk.corpus import LazyCorpusLoader
from nltk.corpus.reader import *
from nltk.tag import *
print "- done"

def main(args):
    initData()
    ####Import desired corpus here###############
    corpus = LazyCorpusLoader('brown', CategorizedTaggedCorpusReader, r'c[a-z]\d\d', cat_file='cats.txt', tag_mapping_function=simplify_brown_tag)
    #############################################
    corpus_stats = corpusstatistics(corpus)
    corpus_fword_frequency = corpus_stats.getRelativeFrequency()
    authors = getAuthors()
    for author in authors:
        for file_ in authors[author]:
            #load text
            text = Data.Data(file_[1]).text
            #tokenize sentences
            text = nltk.sent_tokenize(text)
            #tokenize words
            text = [nltk.word_tokenize(sentence) for sentence in text]
            
            text_fwords = fwords()
            text_fwords.processSentenceWordArray(text)

            text_fword_frequency = text_fwords.relativeFrequency(sum([len([x for x in y if x not in string.punctuation and x[0] != "``" and x[0] != "''"]) for y in text]))
            store(text_fwords.getCount(), text_fword_frequency, author, file_[0])
            
            #nltk.add_logs(logx, logy)
            
            #tag part of speech
            #text = nltk.batch_pos_tag(text)
            #parser = nltk.ViterbiParser()
            
            #print parser.batch_iter_parse(text)
            #print text
        
        #creating sentence structure with POS tagged words
        
        #
        
        #for sentence in text:
            #print sentence
            #print [word[0] for word in sentence if word[1] == "IN"]
    #try:
    #except:
    #    print "error"
    #    return 0
    #else:
    #    return 1
    

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
    
def getAuthors(path = '../documents/'):
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
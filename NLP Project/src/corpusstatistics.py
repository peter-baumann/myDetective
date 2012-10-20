'''
Created on 12.10.2012

@author: Peter
'''
import fwords
import sqlite3
from decimal import *

class corpusstatistics(object):
    '''
    classdocs
    '''
    
    def __init__(self, corpus):
        self.corpus = corpus
    
    def getRelativeFrequency(self, force_update = False):
        '''
        uses the word of fwords and returns the relative frequency of their appearance to
        the number of tokens in the brown corpus, excluding numbers and punctuation (= 1016752)
        '''
        
        #retrieving name of corpus by path
        cor_path = self.corpus.root.split("/")
        ar_size = len(self.corpus.root.split("/"))
        name = cor_path[ar_size - 1] if (ar_size > 0) else "temp"
        force_update = True if name == "temp" else force_update;
        
        #generating and storing new data or using cached values    
        if force_update or not self.isCached(name):
            words = [w.lower() for w in self.corpus.words()]
            cfword = fwords.fwords()
            cfword.processWordArray(words)
            rel_frequencies = cfword.relativeFrequency(1016752) #TODO - count tokens, and use that value
            abs_frequencies = cfword.getCount()
            self.store(abs_frequencies, rel_frequencies, name)
            return rel_frequencies
        else:
            rel_frequencies = self.loadRelativeFrequencies(name)
            abs_frequencies = self.loadAbsoluteFrequencies(name)
    
    def loadAbsoluteFrequencies(self, corpus_name):
        return self.loadFrequencies(corpus_name, True)
    
    def loadRelativeFrequencies(self, corpus_name):
        return self.loadFrequencies(corpus_name, False)
    
    def loadFrequencies(self, corpus_name, is_abs):
        con = sqlite3.connect("../cache.db") #@UndefinedVariable
        #retrieve the id of the corpus
        try:
            with con:
                for row in con.execute("SELECT rowid FROM corpora WHERE name=?", [corpus_name]):
                    corpus_id = row[0]
        except sqlite3.Error, e: #@UndefinedVariable
            print e
        #now retrieve all statistical information from the database
        fword_list = {}
        try:
            with con:
                for row in con.execute("SELECT * FROM corpora_fwords WHERE corpus_id=?", [corpus_id]):
                    for row_ in con.execute("SELECT name FROM fwords WHERE rowid =?", [row[1]]):
                        if is_abs:
                            fword_list.update({str(row_[0]) : row[2]})
                        else:
                            fword_list.update({str(row_[0]) : Decimal(row[3])})
        except sqlite3.Error, e: #@UndefinedVariable
            print e
        return fword_list
    
    
    def store(self, abs_frequencies, rel_frequencies, corpus_name):
        #storing results in database
        con = sqlite3.connect("../cache.db") #@UndefinedVariable
        #Add corpus if not already in db
        try:
            with con:
                con.execute("INSERT INTO corpora(name) VALUES (?)", [corpus_name])
        except sqlite3.IntegrityError: #@UndefinedVariable
            pass
        #get corpus id
        corpus_id = 0
        for row in con.execute("SELECT rowid FROM corpora WHERE name=?", [corpus_name]):
            corpus_id = row[0]
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
        #store values in db
        for key in rel_frequencies.iterkeys():
            try:
                with con:
                    con.execute("INSERT INTO corpora_fwords(corpus_id, fword_id, count, percentage) VALUES (?, ?, ?, ?)", (corpus_id, ids[key], int(abs_frequencies[key]), str(rel_frequencies[key])))
            except sqlite3.IntegrityError: #@UndefinedVariable
                pass
    
    def isCached(self, corpus_name):
        con = sqlite3.connect("../cache.db") #@UndefinedVariable
        cached = False
        #retrieve the id of the corpus
        try:
            with con:
                for row in con.execute("SELECT rowid FROM corpora WHERE name=?", [corpus_name]):
                    cached = True
        except sqlite3.Error, e: #@UndefinedVariable
            print e
        
        print "using cached corpus statistics" if cached else "generating corpus statistics..."
            
        return cached 
        
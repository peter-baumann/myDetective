'''
Created on 06.11.2012

@author: Peter
'''
import sqlite3
class database(object):
    '''
    classdocs
    '''


    def __init__(self):
        pass

    def initData(self):
        #backup of old database if any, for avoiding unintentional data loss
        import os
        if os.path.isfile("../cache.db"):
            from time import time
            os.rename("../cache.db", "../cache_bkp" + str(time()) + ".db")
        #creating database
        conn = sqlite3.connect("../cache.db") #@UndefinedVariable
        cursor = conn.cursor()
#        cursor.execute("CREATE TABLE corpora (name varchar unique , count integer)")
#        cursor.execute("CREATE TABLE fwords (name varchar unique)")
#        cursor.execute("CREATE TABLE corpora_fwords (corpus_id integer, fword_id integer, count integer, percentage text)")
#        cursor.execute("CREATE TABLE authors (name varchar unique)")
#        #TODO : execute once for table creation, store values in db
#        cursor.execute("CREATE TABLE training (filename varchar unique, author_id integer, count integer)")
#        cursor.execute("CREATE TABLE training_fwords (training_id integer, fword_id integer, count integer, percentage text)")
        cursor.execute("CREATE TABLE spellings (word varchar unique, hits integer, suggestion varchar, distance integer)")
        conn.commit()
        cursor.close()
    
    def initWikipediaCache(self):
        #backup of old database if any, for avoiding unintentional data loss
        import os
        if os.path.isfile("../wikipedia.db"):
            from time import time
            os.rename("../wikipedia.db", "../wikipedia_bkp" + str(time()) + ".db")
        #creating database
        conn = sqlite3.connect("../wikipedia.db") #@UndefinedVariable
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE spellings (word varchar unique, hits integer, suggestion varchar, distance integer)")
        conn.commit()
        cursor.close()
    
    def getSpelling(self, word):
        con = sqlite3.connect("../wikipedia.db") #@UndefinedVariable
        for row in con.execute("SELECT word, hits, suggestion, distance FROM spellings WHERE word=?", [word]):
            return [row[0], row[1], row[2], row[3]]
        return None
    
    def saveSpelling(self, word, hits, suggestion = "", distance = 0):
        con = sqlite3.connect("../wikipedia.db") #@UndefinedVariable
        try:
            with con:
                con.execute("INSERT INTO spellings(word, hits, suggestion, distance) VALUES (?,?,?,?)", [word, hits, suggestion, distance])
                return True
        except sqlite3.IntegrityError: #@UndefinedVariable
            return False
    
    def storeFunctionWordFrequencies(self, abs_frequencies, rel_frequencies, author_name, filename):
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
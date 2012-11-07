'''
Created on 27.09.2012

@author: Peter
'''
import operator
print "loading libraries...",
import sys, nltk, os, Data, string, sqlite3, re, math, collections
from fwords import fwords
from corpusstatistics import corpusstatistics
from nltk.corpus import LazyCorpusLoader
from nltk.corpus.reader import *
from nltk.tag import *
from nltk.collocations import *
from subprocess import *
from svmtools.SvmInterface import *
print "- done"

f = False
t = True
settings = {'FunctionWordFrequency' : f, 
            'BigramFrequency' : f, 
            'TrigramFrequency' : f, 
            'AverageWordLength' : t, 
            'AverageSentenceLength' : f, 
            'LexicalDiversity' : f}

# Constants 
class Mode:
    FunctionWordFrequency = 1
    BigramFrequency = 2
    TrigramFrequency = 4
    AverageWordLength = 8
    AverageSentenceLength = 16
    LexicalDiversity = 32

#don't change this
bigramIndices = []
trigramIndices = []
bi_filter =  0
tri_filter = 0
test_method_bi  = [None,None]
test_method_tri = [None,None]
x = nltk.collocations.BigramAssocMeasures()
bi_meassures = {"Raw frequency":x.raw_freq, "Chi-squared":x.chi_sq, "Dice's coefficient":x.dice, "Jaccard Index":x.jaccard, "Likelihood-ratio":x.likelihood_ratio, "Mutual Information":x.mi_like, "Phi coefficient":x.phi_sq, "Pointwise mutual information":x.pmi, "Poisson-stirling":x.poisson_stirling, "Student's-t":x.student_t}
x = nltk.collocations.TrigramAssocMeasures()
tri_meassures = {"Raw frequency":x.raw_freq, "Chi-squared":x.chi_sq, "Jaccard Index":x.jaccard, "Likelihood-ratio":x.likelihood_ratio, "Mutual Information":x.mi_like, "Pointwise mutual information":x.pmi, "Poisson-stirling":x.poisson_stirling, "Student's-t":x.student_t}
training_mode = True
##################

def main(args):
    global training_mode, test_method_bi, test_method_tri
    batchTest()
    #mostWritten()
#    train = "training.lsvm"
#    test = "testing.lsvm"
#    cross_test = "cross.lsvm"
#    print "started..."
#    for mes in bi_meassures:
#        training_mode = True
#        test_method_bi[0] = mes
#        test_method_bi[1] = bi_meassures[mes]
#        #training(train)
#        #testing(test)
#        #svm(train, test)
#        training(cross_test)
#        svm(cross_test)
        
def batchTest():
    '''This function tests all possible combinations of features using cross validation'''
    global t, f, bi_filter, tri_filter
    output = "cross.lsvm"
    authors = getAuthors('../crosstesting/')
    
    print "\n--------------------------------------------------------------------------------"
    print "--Batch Testing of all possible combinations of features with cross validation--"
    print "--This test can take some hours - depending on your CPU and number of documents-"
    print "--------------------------------------------------------------------------------\n"
    print "Testing with: " + str(len(authors)) + " authors and a total of " + str(sum([len(authors[x]) for x in authors])) + " documents\n\n"
    
    print "1) Single Feature Statistics:"
    print "   [a] Average Word Length:"
    cset(f,f,f,t,f,f)
    crosstesting(output)
    
    print "   [b] Average Sentence Length:"
    cset(f,f,f,f,t,f)
    crosstesting(output)
      
    print "   [c] Lexical Diversity:"
    cset(f,f,f,f,f,t)
    crosstesting(output)
    
    print "   [d] Function Word Bigram Frequency using different association measures and frequency filters:"
    cset(f,t,f,f,f,f)
    for mes in bi_meassures:
        for i in range(1, 5):
            bi_filter = i
            test_method_bi[0] = mes
            test_method_bi[1] = bi_meassures[mes]
            print "       " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
        bi_filter = -1 # this tells the function to use adaptive one
        test_method_bi[0] = mes
        test_method_bi[1] = bi_meassures[mes]
        print "       " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
        
    print "   [d] Function Word Trigram Frequency using different association measures and frequency filters:"
    cset(f,f,t,f,f,f)
    for mes in tri_meassures:
        for i in range(1, 5):
            tri_filter = i
            test_method_tri[0] = mes
            test_method_tri[1] = tri_meassures[mes]
            print "       " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
        tri_filter = -1 # this tells the function to use adaptive one
        test_method_tri[0] = mes
        test_method_tri[1] = tri_meassures[mes]
        print "       " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
        
    print "   [f] Function Word Frequency:"
    cset(t,f,f,f,f,f)
    crosstesting(output)
    
    print "Combined Feature Statistics:"

def cset(FunctionWordFrequency, BigramFrequency, TrigramFrequency, AverageWordLength, AverageSentenceLength, LexicalDiversity):
    '''change settings'''
    global settings
    settings['FunctionWordFrequency'] = FunctionWordFrequency
    settings['BigramFrequency'] = BigramFrequency
    settings['TrigramFrequency'] = TrigramFrequency
    settings['AverageWordLength'] = AverageWordLength
    settings['AverageSentenceLength'] = AverageSentenceLength
    settings['LexicalDiversity'] = LexicalDiversity

def crosstesting(filen):
    processAuthorFolder('../crosstesting/', filen)
    svm(filen)
    
def training(filen):
    processAuthorFolder('../training/', filen)
    svm(filen)

def testing(filen):
    global training_mode
    training_mode = False
    processAuthorFolder('../testing/', filen)
    svm(filen)

def svm(train, test = None):
    if (test != None):
        cmd = './svmtools/easy.py "{0}" "{1}"'.format(train, test)
        output = Popen(cmd, shell = True, stdout = PIPE, stderr = None)
        text = output.stdout.read()
        r = re.compile('Accuracy\s=\s(.*?)\s\(classification\)')
        m = r.search(text)
        if m:
            print test_method_bi[0] + ": " + m.group(1)
    else:
        cmd = './svmtools/easy.py "{0}"'.format(train)
        output = Popen(cmd, shell = True, stdout = PIPE, stderr = None)
        text = output.stdout.read()
        r = re.compile(r'CV\srate=(.*?)\n')
        m = r.search(text)
        if m:
            print "------> " + m.group(1) + "%"

def testDocument():
    pass

def processAuthorFolder(input_folder, output_file):
    wfile = open(output_file, "w");
    
    authors = getAuthors(input_folder)
    author_id = 0
    for author in authors:
        author_id += 1
        for file_ in authors[author]:
            wfile.write(listToSVMVector(author_id, getAttributeVector(file_[1])))
    wfile.close()
    
def extractVectors(input_folder):    
    authors = getAuthors(input_folder)
    author_id = 0
    labels = []
    values = []
    author_list = []
    for author in authors:
        author_id += 1
        author_list.append(author)
        for file_ in authors[author]:
            labels.append(author_id)
            values.append(getAttributeVector(file_[1]))

    return labels, values, author_list

def setMode(mode):
    cset(f, f, f, f, f, f)
    atLeast1Mode = False
    # test type
    if mode & Mode.FunctionWordFrequency == Mode.FunctionWordFrequency:
        print "mode 1"
        cset(t,f,f,f,f,f)
        atLeast1Mode = True
    if mode & Mode.BigramFrequency == Mode.BigramFrequency:
        print "mode 2"
        cset(f,f,f,t,f,f)
        atLeast1Mode = True
    if mode & Mode.TrigramFrequency == Mode.TrigramFrequency:
        print "mode 3"
        cset(f,f,f,t,f,f)
        atLeast1Mode = True
    if mode & Mode.AverageWordLength == Mode.AverageWordLength:
        print "mode 4"
        cset(f,f,f,t,f,f)
        atLeast1Mode = True
    if mode & Mode.AverageSentenceLength == Mode.AverageSentenceLength:
        print "mode 5"
        cset(f,f,f,f,t,f)
        atLeast1Mode = True
    if mode & Mode.LexicalDiversity == Mode.LexicalDiversity:
        print "mode 6"
        cset(f,f,f,f,f,t)
        atLeast1Mode = True
    if atLeast1Mode == False:
        print "mode err"
        return    # invalid mode
    
def getAuthors(path = '../training/'):
    """returns a list of authors with corresponding files."""
    authors = collections.OrderedDict()
    author_listing = os.listdir(path)
    for author in author_listing:
        if os.path.isdir(path + author):
            author_path = os.path.join(path, author)
            author_path += "/"
            file_listing = os.listdir(author_path)
            file_listing = [[file_, author_path + file_] for file_ in file_listing]
            if len(file_listing) > 0:
                authors.update({author:file_listing})
    return authors
    
def getAttributeVector(file_name):
    global bigramIndices, training_mode, settings
    text = Data.Data(file_name).text.lower()
    sentences = nltk.sent_tokenize(text)
    words = [x for x in nltk.word_tokenize(text) if x not in string.punctuation and re.search("[0-9]", x) == None and x != "``" and x != "''"]
    
    #punctuation
    
    #part of speech
    
    #lexical diversity
    diversity = [len(words) / float(len(set(words)))] if settings['LexicalDiversity'] else []

    #function word frequency
    if settings['FunctionWordFrequency']:
        fwords = fwordFrequency(words, len(words))
        fword_frequency = [fwords[f] for f in fwords]
    else:
        fword_frequency = []
    
    #average word length
    avg_word = [average_word_length(words)] if settings['AverageWordLength'] else []
    
    #average sentence length
    avg_sent = [average_sentence_length(sentences)] if settings['AverageSentenceLength'] else []
    
    #Function Word Bigram Frequency
    bigram_frequency = BigramFrequencyToUnifiedVector(BigramFrequency(words, test_method_bi[1])) if settings['BigramFrequency'] else []
    
    #Trigram frequencies
    trigram_frequency = TrigramFrequencyToUnifiedVector(TrigramFrequency(words, test_method_tri[1])) if settings['TrigramFrequency'] else []
    
    return diversity + fword_frequency + avg_word + avg_sent + bigram_frequency + trigram_frequency

def bigramsToStringVector(bigrams):
    return {b[0][0] + "_" + b[0][1] : b[1] for b in bigrams}

def trigramsToStringVector(bigrams):
    return {b[0][0] + "_" + b[0][1] + "_" + b[0][2] : b[1] for b in bigrams}

def listToSVMVector(ida, listl):
    """ Transforms dictionary to libsvm readable date """
    out = str(ida)
    for idx, val in enumerate(listl):
        if str(val) != "0": 
            out += " " + str(idx) + ":" + str(val)
    #print out
    out += "\n"
    return out
    
def prepare_ngrams(ngrams):
    """ Prepares the list of n-grams, he or she -> it and so on.
        Input: two-dimensional list of n-grams"""
    for index_ngram, ngram in enumerate(ngrams):
        for index_word, word in enumerate(ngram):
            if word in ["he", "she"]: ngrams[index_ngram][index_word]="it"
            if word in ["his", "hers"]: ngrams[index_ngram][index_word]="its"
    return ngrams


def average_word_length(words):
    """ Calculates the average length of a word in array.
        Will reject all non-words with regular expression."""
    words_total = 0
    length_total = 0
    for word in words:
        if re.match("^[A-Za-z-/]+.?$", word):
            length_total += len(word)
            words_total += 1
    return length_total/float(words_total)

def average_sentence_length(sentences):
    """ Calculates the average length (in words) of a sentence in array."""
    length_total = 0
    for sentence in sentences:
        length_total += len(sentence.split())
    return length_total/float(len(sentences))
    
def fwordFrequency(words, token_count):
    text_fwords = fwords()
    return text_fwords.relativeFrequencyWordArray(words, token_count)

def BigramFrequency(words, test_method):
    global bi_filter
    return_array = []
    finder = BigramCollocationFinder.from_words(words)
    if bi_filter != -1:
        finder.apply_freq_filter(bi_filter)
    else:
        finder.apply_freq_filter(math.ceil(math.log(len(words) - 1) /3) - 1) #@UndefinedVariable
    scored = finder.score_ngrams(test_method)
    for score in scored:
        if(fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1])):
            return_array.append(score)
    return return_array

def BigramFrequencyToUnifiedVector(bg_freq):
    global bigramIndices, training_mode
    bigram_frequency = bigramsToStringVector(bg_freq)
    bigram_vector = []    
    for bigram in bigramIndices:
        if bigram in bigram_frequency.keys():
            bigram_vector.append([bigram,bigram_frequency[bigram]])
            if bigramIndices.index(bigram) != bigram_vector.index([bigram,bigram_frequency[bigram]]):
                print "FAILURE: " + str(bigramIndices.index(bigram)) + " != " + str(bigram_vector.index(bigram))
                sys.exit()
            del bigram_frequency[bigram]
        else:
            bigram_vector.append([bigram,0])
            if bigramIndices.index(bigram) != bigram_vector.index([bigram,0]):
                print "FAILURE: " + str(bigramIndices.index(bigram)) + " != " + str(bigram_vector.index(bigram))
                sys.exit()
    for bigram in bigram_frequency:
        if bigram in bigramIndices:
            print "FAILURE: " + bigram + " should have been removed!"
            sys.exit()
        else:
            if training_mode:
                bigramIndices.append(bigram)
                bigram_vector.append([bigram,bigram_frequency[bigram]])
            else:
                pass
    return [b[1] for b in bigram_vector]
    
def TrigramFrequency(words, test_method):
    global tri_filter
    return_array = []
    finder = TrigramCollocationFinder.from_words(words)
    if tri_filter != -1:
        finder.apply_freq_filter(tri_filter)
    else:
        finder.apply_freq_filter(math.ceil(math.log(len(words) - 1) /3) - 1) #@UndefinedVariable
    scored = finder.score_ngrams(test_method)
    for score in scored:
        if(fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1]) and fwords.isFunctionWord(score[0][2])):
            return_array.append(score)
    return return_array

def TrigramFrequencyToUnifiedVector(bg_freq):
    global trigramIndices, training_mode
    trigram_frequency = trigramsToStringVector(bg_freq)
    trigram_vector = []    
    for trigram in trigramIndices:
        if trigram in trigram_frequency.keys():
            trigram_vector.append([trigram,trigram_frequency[trigram]])
            if trigramIndices.index(trigram) != trigram_vector.index([trigram,trigram_frequency[trigram]]):
                print "FAILURE: " + str(trigramIndices.index(trigram)) + " != " + str(trigram_vector.index(trigram))
                sys.exit()
            del trigram_frequency[trigram]
        else:
            trigram_vector.append([trigram,0])
            if trigramIndices.index(trigram) != trigram_vector.index([trigram,0]):
                print "FAILURE: " + str(trigramIndices.index(trigram)) + " != " + str(trigram_vector.index(trigram))
                sys.exit()
    for trigram in trigram_frequency:
        if trigram in trigramIndices:
            print "FAILURE: " + trigram + " should have been removed!"
            sys.exit()
        else:
            if training_mode:
                trigramIndices.append(trigram)
                trigram_vector.append([trigram,trigram_frequency[trigram]])
            else:
                pass
    return [b[1] for b in trigram_vector]  

#just a helper function for finding the students with the most text data
def mostWritten():
    authors = {}
    files = os.listdir("../CORPUS_TXT/")
    for filed in files:
        if filed[len(filed)-3:len(filed)] == "txt" and "Freq" not in filed:
            size = os.path.getsize("../CORPUS_TXT/" + filed)
            author = filed[0:len(filed)-5]
            if author in authors:
                authors[author][0] = authors[author][0] + size
                authors[author][1] = authors[author][1] + 1
            else:
                authors.update({author:[size, 1]})
                
    authors2 = sorted(authors.items(), key=operator.itemgetter(1), reverse=True)
    print authors2
    authors = sorted(authors.items(), key=lambda (k, v): operator.itemgetter(1)(v), reverse=True)
    print authors


def get_essay_vectors(unknown=None):
    """
    Generates dictionary of authors/essays/measures
    used by PCA
    """
    
    global bi_filter, test_method_bi, test_method_tri

    bi_filter = -1 #this will use the adaptive version of frequency filtering. E.g. if it is set to 2, bigrams have to appear at least twice in a text to be counted.

    test_method_bi  = ["Raw frequency", bi_meassures["Raw frequency"]]
    test_method_tri  = ["Raw frequency", tri_meassures["Raw frequency"]]


    global settings
    settings = {'FunctionWordFrequency' : True,
        'BigramFrequency' : True,
        'TrigramFrequency' : False,
        'AverageWordLength' : True,
        'AverageSentenceLength' : True,
        'LexicalDiversity' : True}

    authors = getAuthors()
    essay_vectors = {}
    for author, data in authors.iteritems():
        essay_vectors[author] = {}
        for file in data:
            # convert all items to float, because PCA library does not
            # like the decimal.Decimal type
            vector = [float(i) for i in getAttributeVector(file[1])]
            essay_vectors[author][file[0]]=vector
        
    if unknown:
        vector = [float(i) for i in getAttributeVector(unknown)]
        essay_vectors["unknown"] = {}
        essay_vectors["unknown"]["unknown"] = vector
        
    return essay_vectors


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

#if __name__ == '__main__':
    #main(sys.exit(main(sys.argv)))    
    
def corpusStuff(init = False):
    #change this for loading another training corpus:
    corpus = LazyCorpusLoader('brown', CategorizedTaggedCorpusReader, 
                              r'c[a-z]\d\d', cat_file='cats.txt', 
                              tag_mapping_function=simplify_brown_tag)
    
    #change this for using a different test method.
    test_method_bi  = nltk.collocations.BigramAssocMeasures().pmi
    test_method_tri = nltk.collocations.TrigramAssocMeasures().pmi
    corpus_stats = corpusstatistics(corpus)
    corpus_fword_frequency = corpus_stats.getRelativeFunctionWordFrequency()
    corpus_bigram_frequency = corpus_stats.getBigramFrequency(test_method_bi)
    
#main()

def getBestModel(authorPath):
    modes = [Mode.AverageSentenceLength, Mode.AverageWordLength, Mode.BigramFrequency, Mode.FunctionWordFrequency, Mode.LexicalDiversity, Mode.TrigramFrequency]

if __name__ == '__main__':
    main()

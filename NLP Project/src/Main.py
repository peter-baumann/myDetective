'''
Created on 27.09.2012

@author: Peter
'''
import operator
import itertools
print "loading libraries...",
import sys, nltk, os, Data, string, re, math, collections, urllib2, time, shutil
from fwords import fwords
from database import database #@UnresolvedImport
from decimal import *
from corpusstatistics import corpusstatistics
from nltk.corpus import LazyCorpusLoader
from nltk.corpus.reader import *
from nltk.tag import *
from nltk.collocations import *
from subprocess import *
from nltk.corpus import wordnet as wn
from svmtools.SvmInterface import *
print "- done"

f = False
t = True
settings = {'FunctionWordFrequency' : f, 
            'BigramFrequency' : f, 
            'TrigramFrequency' : f, 
            'AverageWordLength' : f, 
            'AverageSentenceLength' : f, 
            'LexicalDiversity' : f,
            'spellingMistakes' : f,
            'punctuation' : f,
            'PartOfSpeechUnigram' : f,
            'PartOfSpeechBigram' : f,
            'PartOfSpeechTrigram' : f}

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
spell_filter = 0
test_method_bi  = [None,None]
test_method_tri = [None,None]
x = nltk.collocations.BigramAssocMeasures()
bi_meassures = {"Raw frequency":x.raw_freq, "Chi-squared":x.chi_sq, "Dice's coefficient":x.dice, "Jaccard Index":x.jaccard, "Likelihood-ratio":x.likelihood_ratio, "Mutual Information":x.mi_like, "Phi coefficient":x.phi_sq, "Pointwise mutual information":x.pmi, "Poisson-stirling":x.poisson_stirling, "Student's-t":x.student_t}
x = nltk.collocations.TrigramAssocMeasures()
tri_meassures = {"Raw frequency":x.raw_freq, "Chi-squared":x.chi_sq, "Jaccard Index":x.jaccard, "Likelihood-ratio":x.likelihood_ratio, "Mutual Information":x.mi_like, "Pointwise mutual information":x.pmi, "Poisson-stirling":x.poisson_stirling, "Student's-t":x.student_t}
training_mode = True
db = database()
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
word_list = []
spellVector = []
pos_vector = []
author_limit = []


#cache for batch - if same feature several times calculated, this will be used to save cpu time
feature_cache = {}
enable_caching = t
bigram_cache = {}
trigram_cache = {}
##################

def main(args = None):
    '''just the main function'''
    global training_mode, test_method_bi, test_method_tri
    if (args != None):
        batchTest()
    
def batchTest():
    '''This function allows testing of all possible combinations of features using cross validation and is meant to be used by researchers'''
    global t, f, bi_filter, tri_filter, spell_filter, settings, test_method_bi, test_method_tri, enable_caching, author_limit
    output = "cross.lsvm"
    authors = getAuthors('../crosstesting/')
    
    print "\n--------------------------------------------------------------------------------"
    print "--Batch Testing of all possible combinations of features with cross validation--"
    print "--This test can take many hours - depending on your CPU and number of documents-"
    print "--------------------------------------------------------------------------------\n"
    print "Testing with: " + str(len(authors)) + " authors and a total of " + str(sum([len(authors[x]) for x in authors])) + " documents\n\n"
    
        #authors = author_limit
    #for i in [5, 15, 30, 50, 75, 100]:
        #author_limit = authors[:i]
    print str(len(author_limit)) + " authors:"
    crosstesting(output)
    #author_limit = authors
    
    mostWritten()
    print "1) Single Feature Statistics:"
    print "   [a] Average Word Length:"
    cset(f,f,f,t)
    crosstesting(output)
    
    print "   [b] Average Sentence Length:"
    cset(f,f,f,f,t)
    crosstesting(output)
      
    print "   [c] Lexical Diversity:"
    cset(f,f,f,f,f,t)
    crosstesting(output)
    
    
    print "   [d] Punctuation Frequency:"
    cset(f,f,f,f,f,f,f,t)
    crosstesting(output)
    
    enable_caching = f
    print "   [d] spelling mistakes with frequency filter:"
    cset(f,f,f,f,f,f,t)
    for i in range(1, 5):
        print "freq: >=" + str(i) + ":"
        spell_filter = i
        crosstesting(output)    
    
    print "   [e] Function Word Frequency:"
    print "       1. Simple Frequency Statistics:"
    cset(t)
    crosstesting(output)
        
    
    print "       2. Bigram Frequency Statistics using different association measures and frequency filters:"
    cset(f,t)
    for mes in bi_meassures:
        for i in range(1, 5):
            bi_filter = i
            test_method_bi[0] = mes
            test_method_bi[1] = bi_meassures[mes]
            print "          " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
        bi_filter = -1 # this tells the function to use adaptive one
        test_method_bi[0] = mes
        test_method_bi[1] = bi_meassures[mes]
        print "          " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
        
    print "       3. Trigram Frequency Statistics using different association measures and frequency filters:"
    cset(f,f,t)
    for mes in tri_meassures:
        for i in range(1, 5):
            tri_filter = i
            test_method_tri[0] = mes
            test_method_tri[1] = tri_meassures[mes]
            print "          " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
        tri_filter = -1 # this tells the function to use adaptive one
        test_method_tri[0] = mes
        test_method_tri[1] = tri_meassures[mes]
        print "          " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
    
    print "   [f] Part of Speech:"
    print "       1. Simple Frequency Statistics:"
    cset(f,f,f,f,f,f,f,f,t)
    crosstesting(output)
    

    enable_caching = t
    print "       2. Bigram Frequency Statistics using different association measures and frequency filters:"
    cset(f,f,f,f,f,f,f,f,f,t)
    for mes in bi_meassures:
        for i in range(1, 5):
            t0 = time.time()
            bi_filter = i
            test_method_bi[0] = mes
            test_method_bi[1] = bi_meassures[mes]
            print "          " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
            print "processing time: " + str(time.time() - t0) + " seconds"
        t0 = time.time()
        bi_filter = -1 # this tells the function to use adaptive one
        test_method_bi[0] = mes
        test_method_bi[1] = bi_meassures[mes]
        print "          " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
        print "processing time: " + str(time.time() - t0) + " seconds"
    
    enable_caching = t
    print "       3. Trigram Frequency Statistics using different association measures and frequency filters:"
    cset(f,f,f,f,f,f,f,f,f,f,t)
    for mes in tri_meassures:
        for i in range(1, 5):
            t0 = time.time()
            tri_filter = i
            test_method_tri[0] = mes
            test_method_tri[1] = tri_meassures[mes]
            print "          " + mes + " with frequency filter = " + str(i) + ":"
            crosstesting(output)
            print "processing time: " + str(time.time() - t0) + " seconds"
        t0 = time.time()
        tri_filter = -1 # this tells the function to use adaptive one
        test_method_tri[0] = mes
        test_method_tri[1] = tri_meassures[mes]
        print "          " + mes + " with adaptive frequency filter based on text length:"
        crosstesting(output)
        print "processing time: " + str(time.time() - t0) + " seconds"
      
  
    enable_caching = t
    print "2) Combined Feature Statistics:"
    
    #using best results from previous test runs
    bi_filter =  -1
    tri_filter = 1
    test_method_bi  = ["Raw frequency", bi_meassures["Raw frequency"]]
    test_method_tri = ["Pointwise mutual information",tri_meassures["Pointwise mutual information"]]
    ###########################################

    for i in range(2, len(settings.keys()) + 1):
        print "   combinations of " + str(i) + " features:"
        for x in itertools.combinations(settings.keys(), i):
            print " - ".join(x) + ":"
            cset()
            for key in x:
                settings[key] = t
            crosstesting(output)    

def posUnigram(sentences):
    '''returns frequencies about part of speech tags'''
    global pos_vector
    tags = partOfSpeechVector(sentences)
    tags = filter (lambda a: a != "EOS" and a != "SOS", tags)
    size = len(tags)
    return_vector = []    
    
    for pos in pos_vector:
        return_vector.append(Decimal(tags.count(pos)) / Decimal(size))
        tags = filter (lambda a: a != pos, tags)
    seen = []
    for pos in tags:
        if pos not in seen:
            seen.append(pos)
            pos_vector.append(pos)
            return_vector.append(Decimal(tags.count(pos)) / Decimal(size))
    #print return_vector
    return return_vector
        
    
def posBigram(sentences, file_name = ""):
    '''returns frequencies about part of speech tag bigrams'''
    return BigramFrequencyToUnifiedVector(BigramFrequency(partOfSpeechVector(sentences), test_method_bi[1], True, file_name))

def posTrigram(sentences, file_name = ""):
    '''returns frequencies about part of speech tag trigrams'''
    return TrigramFrequencyToUnifiedVector(TrigramFrequency(partOfSpeechVector(sentences), test_method_tri[1], True, file_name))

def partOfSpeechVector(sentences):
    '''Creates a list of pos tags of given sentences'''
    tagged = nltk.batch_pos_tag(sentences)
    tags = []
    for sentence in tagged:
        td = [w[1] for w in sentence]
        td.append("EOS") #add end of sentence "tag"
        td.reverse()
        td.append("SOS") #add start of sentence "tag"
        td.reverse()
        for t in td:
            if all(c in string.letters for c in t):
                tags.append(t)
    return tags

def spellingVector(words):
    '''creates the feature vector of spelling mistakes for libsvm'''
    global spellVector, spell_filter
    tokens = [w for w in words if isMissSpelled(w)]
    types = set(tokens)
    filtered = []
    
    #Only consider words that appear for at least a certain threshold value spell_filter
    for typ in types:
        if tokens.count(typ) >= spell_filter:
            filtered.append(typ)

    spelling_mistakes = []
    
    for spell in spellVector:
        if spell in filtered:
            spelling_mistakes.append(1)
        else:
            spelling_mistakes.append(0)
    
    for typ in filtered:
        spelling_mistakes.append(1)
        spellVector.append(typ)
    
    return spelling_mistakes
    

def getWikipediaInformation(word):
    '''lookups a word in wikipedia. If already looked up before, use cached values from database'''
    inf = db.getSpelling(word)
    if inf == None:
        try:
            page = opener.open("http://en.wikipedia.org/w/api.php?action=query&format=xml&list=search&srsearch=" + word + "&srprop=timestamp").read()
            r1 = re.compile(r"totalhits=\"(.*?)\"")
            r2 = re.compile(r"suggestion=\"(.*?)\"")
            m = [r1.search(page), r2.search(page)]
            if m[0]:
                if m[1]:
                    distance = nltk.distance.edit_distance(word, m[1].group(1))
                    db.saveSpelling(word, m[0].group(1), m[1].group(1), distance)
                else:
                    db.saveSpelling(word, m[0].group(1))
            else:
                return None
        except:
            return None
    else:
        return inf


def missSpelledFunctionWord(word):
    #adaptive word distance limit depending on length of word
    '''Decides if a word may be misspelled using wordnet'''
    if (len(word) > 1 and 
        len(set(word) & set(string.letters)) > 0 and 
        wn.morphy(word) == None and                     #@UndefinedVariable
        len(wn.synsets(word)) == 0 and                  #@UndefinedVariable
        not fwords.isFunctionWord(word)):
        
            lim = math.ceil(math.log(len(word))) - 1 #@UndefinedVariable
            if len(word) > 4:
                if distToFuncWords(word) <= lim:
                    return True
            return False
    else:
        return False
        

def isMissSpelled(word):
    '''decides whether a word is misspelled or not, based on wikipedia information'''
    try:
        if (len(word) > 1 and 
            len(set(word) & set(string.letters)) > 0 and 
            wn.morphy(word) == None and                     #@UndefinedVariable
            len(wn.synsets(word)) == 0 and                  #@UndefinedVariable
            not fwords.isFunctionWord(word) and
            len(word.split("-")) == 1):
            
            word_data = getWikipediaInformation(word)
            if word_data == None:
                return False
            hits = int(word_data[1])
            suggestion = word_data[2]
            distance = int(word_data[3])

            if suggestion != "":
                return True
            else:
                if distToFuncWords(word) < 3:
                    return True
                else:
                    return False                    
        else:
            return False
    except:
        return False

def distToFuncWords(word):
    '''returns a words smallest levenshtein distance to words in a set of function words'''
    return min([nltk.distance.edit_distance(word, fw) for fw in fwords().getWords()])


def cset(FunctionWordFrequency = False, BigramFrequency = False, 
         TrigramFrequency = False, AverageWordLength = False, 
         AverageSentenceLength = False, LexicalDiversity = False, 
         spellingMistakes = False, punctuation = False,
         partOfSpeechUnigram = False, PartOfSpeechBigram = False,
         PartOfSpeechTrigram = False):
    '''change settings for which features to be selected for authorship attribution'''
    global settings
    settings['FunctionWordFrequency'] = FunctionWordFrequency
    settings['BigramFrequency'] = BigramFrequency
    settings['TrigramFrequency'] = TrigramFrequency
    settings['AverageWordLength'] = AverageWordLength
    settings['AverageSentenceLength'] = AverageSentenceLength
    settings['LexicalDiversity'] = LexicalDiversity
    settings['spellingMistakes'] = spellingMistakes
    settings['punctuation'] = punctuation
    settings['PartOfSpeechUnigram'] = partOfSpeechUnigram
    settings['PartOfSpeechBigram'] = PartOfSpeechBigram
    settings['PartOfSpeechTrigram'] = PartOfSpeechTrigram

def crosstesting(filen):
    '''crosstesting a set of documents'''
    global bigramIndices, trigramIndices
    bigramIndices = []
    trigramIndices = []
    processAuthorFolder('../crosstesting/', filen)
    svm(filen)
    
def training(filen):
    '''training some documents'''
    processAuthorFolder('../training/', filen)
    svm(filen)

def testing(filen):
    '''testing some documents'''
    global training_mode
    training_mode = False
    processAuthorFolder('../testing/', filen)
    svm(filen)

def svm(train, test = None):
    '''Executes libsvm'''
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

def processAuthorFolder(input_folder, output_file):
    '''Writes all feature vectors of each text from each author into a .lsvm file'''
    wfile = open(output_file, "w");    
    authors = getAuthors(input_folder)
    author_id = 0
    for author in authors:
        author_id += 1
        for file_ in authors[author]:
            wfile.write(listToSVMVector(author_id, getAttributeVector(file_[1])))
    wfile.close()
    
def extractVectors(input_folder):
    '''unknown functionality. not used. to be deleted'''   
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
    global author_limit
    authors = collections.OrderedDict()
    author_listing = os.listdir(path)
    for author in author_listing:
        if os.path.isdir(path + author):
            author_path = os.path.join(path, author)
            author_path += "/"
            file_listing = os.listdir(author_path)
            file_listing = [[file_, author_path + file_] for file_ in file_listing]
            if len(file_listing) > 0:
                if author_limit == []:
                    authors.update({author:file_listing})
                else:
                    if author in author_limit:
                        authors.update({author:file_listing})
    return authors

def getTextAttributes(file_name):
    '''function to retrieve the text, sentences and words. Check if text loaded already before calling this function to save performance'''
    text = Data.Data(file_name).text.lower()
    sentences = nltk.sent_tokenize(text)
    pattern = re.compile('[\.\'\/]+')
    words = [pattern.sub('', x) for x in nltk.word_tokenize(text) if x not in string.punctuation and re.search("[0-9]", x) == None and x != "``" and x != "''"]
    return {"text": text, "sentences": sentences, "words": words}

def getAttributeVector(file_name):
    '''returns a Vector of the values of all enabled features. Several feature combinations are possible. Use cset for defining which'''
    global bigramIndices, training_mode, settings, feature_cache, enable_caching, t0
    text = ""
    words = []
    sentences = []
    
    #punctuation
    if settings['punctuation']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('punctuation'):
                punctuation = feature_cache[file_name]['punctuation']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                punctuation = punctuationVector(text) 
                feature_cache[file_name].update({'punctuation' : punctuation})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            punctuation = punctuationVector(text) 
            feature_cache.update({file_name:{'punctuation' : punctuation}})
    else: 
        punctuation = []
    
    #spelling mistakes
    if settings['spellingMistakes']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('spellingMistakes'):
                spelling = feature_cache[file_name]['spellingMistakes']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                spelling = spellingVector(words)
                feature_cache[file_name].update({'spellingMistakes' : spelling})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            spelling = spellingVector(words)
            feature_cache.update({file_name:{'spellingMistakes' : spelling}})
    else: 
        spelling = []
    
    #lexical diversity
    if settings['LexicalDiversity']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('LexicalDiversity'):
                diversity = feature_cache[file_name]['LexicalDiversity']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                diversity = [len(words) / float(len(set(words)))]
                feature_cache[file_name].update({'LexicalDiversity' : diversity})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            diversity = [len(words) / float(len(set(words)))]
            feature_cache.update({file_name:{'LexicalDiversity' : diversity}})
    else: 
        diversity = []

    #function word frequency
    if settings['FunctionWordFrequency']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('FunctionWordFrequency'):
                fword_frequency = feature_cache[file_name]['FunctionWordFrequency']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                fwords = fwordFrequency(words, len(words))
                fword_frequency = [fwords[f] for f in fwords]
                feature_cache[file_name].update({'FunctionWordFrequency' : fword_frequency})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            fwords = fwordFrequency(words, len(words))
            fword_frequency = [fwords[f] for f in fwords]
            feature_cache.update({file_name:{'FunctionWordFrequency' : fword_frequency}})
    else: 
        fword_frequency = []
    
    #average word length
    if settings['AverageWordLength']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('AverageWordLength'):
                avg_word = feature_cache[file_name]['AverageWordLength']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                avg_word = [average_word_length(words)]
                feature_cache[file_name].update({'AverageWordLength' : avg_word})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            avg_word = [average_word_length(words)]
            feature_cache.update({file_name:{'AverageWordLength' : avg_word}})
    else: 
        avg_word = []
    
    #average sentence length
    if settings['AverageSentenceLength']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('AverageSentenceLength'):
                avg_sent = feature_cache[file_name]['AverageSentenceLength']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                avg_sent = [average_sentence_length(sentences)]
                feature_cache[file_name].update({'AverageSentenceLength' : avg_sent})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            avg_sent = [average_sentence_length(sentences)]
            feature_cache.update({file_name:{'AverageSentenceLength' : avg_sent}})
    else: 
        avg_sent = []
        
    #Function Word Bigram Frequency
    if settings['BigramFrequency']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('BigramFrequency'):
                if feature_cache[file_name]['BigramFrequency'].has_key(test_method_bi[0]):
                    if feature_cache[file_name]['BigramFrequency'][test_method_bi[0]].has_key(str(bi_filter)):
                        bigram_frequency = BigramFrequencyToUnifiedVector(feature_cache[file_name]['BigramFrequency'][test_method_bi[0]][str(bi_filter)])
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                bigram_frequency = BigramFrequencyToUnifiedVector(BigramFrequency(words, test_method_bi[1]))
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            bigram_frequency = BigramFrequencyToUnifiedVector(BigramFrequency(words, test_method_bi[1]))
    else: 
        bigram_frequency = []
    
    #Function Word Trigram frequencies
    if settings['TrigramFrequency']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('TrigramFrequency'):
                if feature_cache[file_name]['TrigramFrequency'].has_key(test_method_tri[0]):
                    if feature_cache[file_name]['TrigramFrequency'][test_method_tri[0]].has_key(str(tri_filter)):
                            trigram_frequency = TrigramFrequencyToUnifiedVector(feature_cache[file_name]['TrigramFrequency'][test_method_tri[0]][str(tri_filter)])
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                trigram_frequency = TrigramFrequencyToUnifiedVector(TrigramFrequency(words, test_method_tri[1]))
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            trigram_frequency = TrigramFrequencyToUnifiedVector(TrigramFrequency(words, test_method_tri[1]))
    else: 
        trigram_frequency = []
    
    #PartOfSpeech Unigrams
    if settings['PartOfSpeechUnigram']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('PartOfSpeechUnigram'):
                part_of_speech_unigram = feature_cache[file_name]['PartOfSpeechUnigram']
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                part_of_speech_unigram = posUnigram([nltk.word_tokenize(snt) for snt in sentences])
                feature_cache[file_name].update({'PartOfSpeechUnigram' : part_of_speech_unigram})
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            part_of_speech_unigram = posUnigram([nltk.word_tokenize(snt) for snt in sentences])
            feature_cache.update({file_name:{'PartOfSpeechUnigram' : part_of_speech_unigram}})
    else: 
        part_of_speech_unigram = []
        
    #PartOfSpeech Bigrams
    if settings['PartOfSpeechBigram']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('PartOfSpeechBigram'):
                if feature_cache[file_name]['PartOfSpeechBigram'].has_key(test_method_bi[0]):
                    if feature_cache[file_name]['PartOfSpeechBigram'][test_method_bi[0]].has_key(str(bi_filter)):
                        part_of_speech_bigram = BigramFrequencyToUnifiedVector(feature_cache[file_name]['PartOfSpeechBigram'][test_method_bi[0]][str(bi_filter)])
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                part_of_speech_bigram = posBigram([nltk.word_tokenize(snt) for snt in sentences], file_name)
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            part_of_speech_bigram = posBigram([nltk.word_tokenize(snt) for snt in sentences], file_name)
    else: 
        part_of_speech_bigram = []
    
    #PartOfSpeech Trigrams
    if settings['PartOfSpeechTrigram']:
        if enable_caching and feature_cache.has_key(file_name):
            if feature_cache[file_name].has_key('PartOfSpeechTrigram'):
                if feature_cache[file_name]['PartOfSpeechTrigram'].has_key(test_method_tri[0]):
                    if feature_cache[file_name]['PartOfSpeechTrigram'][test_method_tri[0]].has_key(str(tri_filter)):
                        part_of_speech_trigram = TrigramFrequencyToUnifiedVector(feature_cache[file_name]['PartOfSpeechTrigram'][test_method_tri[0]][str(tri_filter)])
            else:
                if text == "":
                    temp = getTextAttributes(file_name)
                    text = temp["text"]
                    words = temp["words"]
                    sentences = temp["sentences"]
                part_of_speech_trigram = posTrigram([nltk.word_tokenize(snt) for snt in sentences], file_name)
        else:
            if text == "":
                temp = getTextAttributes(file_name)
                text = temp["text"]
                words = temp["words"]
                sentences = temp["sentences"]
            part_of_speech_trigram = posTrigram([nltk.word_tokenize(snt) for snt in sentences], file_name)
    else: 
        part_of_speech_trigram = []
    
    #returning combined vector of all features that have been selected.
    return (diversity + fword_frequency + avg_word + avg_sent + bigram_frequency + trigram_frequency + 
            spelling + part_of_speech_unigram + part_of_speech_bigram + part_of_speech_trigram + punctuation)

def bigramsToStringVector(bigrams):
    '''combines the 2 tokens of a bigram to one single string to use in a dictionary'''
    return {b[0][0] + "_" + b[0][1] : b[1] for b in bigrams}

def trigramsToStringVector(bigrams):
    '''combines the 3 tokens of a trigram to one single string to use in a dictionary'''
    return {b[0][0] + "_" + b[0][1] + "_" + b[0][2] : b[1] for b in bigrams}

def listToSVMVector(ida, listl):
    """ Transforms dictionary to libsvm readable data """
    out = str(ida)
    for idx, val in enumerate(listl):
        if str(val) != "0": 
            out += " " + str(idx) + ":" + str(val)
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
        length_total += len(nltk.word_tokenize(sentence))
    return length_total/float(len(sentences))
    
def fwordFrequency(words, token_count):
    '''retrieve relative function word frequencies'''
    text_fwords = fwords()
    return text_fwords.relativeFrequencyWordArray(words, token_count)

def BigramFrequency(words, test_method, pos = False, file_name = ""):
    '''returns the meassured bigram frequencies for a file'''
    global bi_filter, feature_cache
    index = 'PartOfSpeechBigram' if pos else 'BigramFrequency'
    return_array = []
    finder = BigramCollocationFinder.from_words(words)
    
    if not feature_cache.has_key(file_name):
        feature_cache[file_name] = {}
    if not feature_cache[file_name].has_key(index):
        feature_cache[file_name][index] = {}
            
    key = ""
    
    for i in range(1, 5):
        for mes in bi_meassures:
            temp_array = []
            if bi_meassures[mes] == test_method:
                key = mes
            if not feature_cache[file_name][index].has_key(mes):
                feature_cache[file_name][index][mes] = {}
            finder.apply_freq_filter(i)
            scored = finder.score_ngrams(bi_meassures[mes])
            for score in scored:
                if pos or (fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1])):
                    temp_array.append(score)
            feature_cache[file_name][index][mes][str(i)] = temp_array
            if (math.ceil(math.log(len(words) - 1) /3) - 1) == i: #@UndefinedVariable
                feature_cache[file_name][index][mes]["-1"] = temp_array

    return feature_cache[file_name][index][key][str(bi_filter)]

def BigramFrequencyToUnifiedVector(bg_freq):
    '''Takes a list of bigram frequencies and returns a vector for libsvm'''
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

def TrigramFrequency(words, test_method, pos = False, file_name = ""):
    '''returns the meassured trigram frequencies for a file'''
    global tri_filter, feature_cache
    index = 'PartOfSpeechTrigram' if pos else 'TrigramFrequency'
    return_array = []
    finder = TrigramCollocationFinder.from_words(words)
    
    if not feature_cache.has_key(file_name):
        feature_cache[file_name] = {}
    if not feature_cache[file_name].has_key(index):
        feature_cache[file_name][index] = {}
            
    key = ""    
    for i in range(1, 5):
        for mes in tri_meassures:
            temp_array = []
            if tri_meassures[mes] == test_method:
                key = mes
            if not feature_cache[file_name][index].has_key(mes):
                feature_cache[file_name][index][mes] = {}
            finder.apply_freq_filter(i)
            scored = finder.score_ngrams(tri_meassures[mes])
            for score in scored:
                if pos or (fwords.isFunctionWord(score[0][0]) and fwords.isFunctionWord(score[0][1])):
                    temp_array.append(score)
            feature_cache[file_name][index][mes][str(i)] = temp_array
            if (math.ceil(math.log(len(words) - 1) /3) - 1) == i: #@UndefinedVariable
                feature_cache[file_name][index][mes]["-1"] = temp_array

    return feature_cache[file_name][index][key][str(tri_filter)]


def TrigramFrequencyToUnifiedVector(bg_freq):
    '''Takes a list of trigram frequencies and returns a vector for libsvm'''
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

def punctuationVector(text):
    '''returns a vector with punctuation statistics from a text'''
    allc = len(text)
    return [Decimal(text.count(".")) / Decimal(allc), 
            Decimal(text.count(",")) / Decimal(allc), 
            Decimal(text.count("?")) / Decimal(allc), 
            Decimal(text.count("!")) / Decimal(allc), 
            Decimal(text.count(":")) / Decimal(allc), 
            Decimal(text.count(";")) / Decimal(allc), 
            Decimal(text.count("-")) / Decimal(allc)]


#just a helper function for finding the students with the most text data
def mostWritten():
    '''retrieves the authors, that wrote the most. Used for Corpus creation.'''
    global author_limit
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
    author_limit =  [x[0] for x in authors2]
    
    
def createAuthorsFromCorpus():
    '''Function that creates a structure of authors from the BAWE corpus. Used for Corpus creation'''
    authors = {}
    files = os.listdir("../CORPUS_TXT/")
    for filed in files:
        if filed[len(filed)-3:len(filed)] == "txt" and "Freq" not in filed:
            size = os.path.getsize("../CORPUS_TXT/" + filed)
            author = filed[0:len(filed)-5]
            if not os.path.exists("../100s/" + author):
                os.makedirs("../100s/" + author)
            if author in authors:
                authors[author][0] = authors[author][0] + size
                authors[author][1] = authors[author][1] + 1
            else:
                authors.update({author:[size, 1]})
            shutil.copy2("../CORPUS_TXT/" + filed, "../100s/" + author + "/" + filed)
                
    #authors2 = sorted(authors.items(), key=operator.itemgetter(1), reverse=True)

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

#if __name__ == '__main__':
    #main(sys.exit(main(sys.argv)))    
    
def corpusStuff(init = False):
    '''This function is deprecated'''
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

def getBestModel(authorPath):
    modes = [Mode.AverageSentenceLength, Mode.AverageWordLength, Mode.BigramFrequency, Mode.FunctionWordFrequency, Mode.LexicalDiversity, Mode.TrigramFrequency]

if __name__ == '__main__':
    main()

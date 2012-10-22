'''
Created on 12.10.2012

@author: Peter
'''
from decimal import *
getcontext().prec = 60

class fwords(object):
    '''
   This class defines the scope of function word recognition
    '''

    def __init__(self):
        self.adverbs = {"again": 0, "ago": 0, "almost": 0, "already": 0, "also": 0, "always": 0, "anywhere": 0, "back": 0, "else": 0, "even": 0, "ever": 0, "everywhere": 0, "far": 0, "hence": 0, "here": 0, "hither": 0, "how": 0, "however": 0, "near": 0, "nearby": 0, "nearly": 0, "never": 0, "not": 0, "now": 0, "nowhere": 0, "often": 0, "only": 0, "quite": 0, "rather": 0, "sometimes": 0, "somewhere": 0, "soon": 0, "still": 0, "then": 0, "thence": 0, "there": 0, "therefore": 0, "thither": 0, "thus": 0, "today": 0, "tomorrow": 0, "too": 0, "underneath": 0, "very": 0, "when": 0, "whence": 0, "where": 0, "whither": 0, "why": 0, "yes": 0, "yesterday": 0, "yet": 0}
        self.auxillaries = {"am": 0, "are": 0, "aren't": 0, "be": 0, "been": 0, "being": 0, "can": 0, "can't": 0, "could": 0, "couldn't": 0, "did": 0, "didn't": 0, "do": 0, "does": 0, "doesn't": 0, "doing": 0, "done": 0, "don't": 0, "get": 0, "gets": 0, "getting": 0, "got": 0, "had": 0, "hadn't": 0, "has": 0, "hasn't": 0, "have": 0, "haven't": 0, "having": 0, "he'd": 0, "he'll": 0, "he's": 0, "i'd": 0, "i'll": 0, "i'm": 0, "is": 0, "i've": 0, "isn't": 0, "it's": 0, "may": 0, "might": 0, "must": 0, "mustn't": 0, "ought": 0, "oughtn't": 0, "shall": 0, "shan't": 0, "she'd": 0, "she'll": 0, "she's": 0, "should": 0, "shouldn't": 0, "that's": 0, "they'd": 0, "they'll": 0, "they're": 0, "was": 0, "wasn't": 0, "we'd": 0, "we'll": 0, "were": 0, "we're": 0, "weren't": 0, "we've": 0, "will": 0, "won't": 0, "would": 0, "wouldn't": 0, "you'd": 0, "you'll": 0, "you're": 0, "you've": 0}
        self.prep_conj = {"about": 0, "above": 0, "after": 0, "along": 0, "although": 0, "among": 0, "and": 0, "around": 0, "as": 0, "at": 0, "before": 0, "below": 0, "beneath": 0, "beside": 0, "between": 0, "beyond": 0, "but": 0, "by": 0, "down": 0, "during": 0, "except": 0, "for": 0, "from": 0, "if": 0, "in": 0, "into": 0, "near": 0, "nor": 0, "of": 0, "off": 0, "on": 0, "or": 0, "out": 0, "over": 0, "round": 0, "since": 0, "so": 0, "than": 0, "that": 0, "though": 0, "through": 0, "till": 0, "to": 0, "towards": 0, "under": 0, "unless": 0, "until": 0, "up": 0, "whereas": 0, "while": 0, "with": 0, "within": 0, "without": 0}
        self.determiners = {"a": 0, "all": 0, "an": 0, "another": 0, "any": 0, "anybody": 0, "anything": 0, "both": 0, "each": 0, "either": 0, "enough": 0, "every": 0, "everybody": 0, "everyone": 0, "everything": 0, "few": 0, "fewer": 0, "he": 0, "her": 0, "hers": 0, "herself": 0, "him": 0, "himself": 0, "his": 0, "i": 0, "it": 0, "its": 0, "itself": 0, "less": 0, "many": 0, "me": 0, "mine": 0, "more": 0, "most": 0, "much": 0, "my": 0, "myself": 0, "neither": 0, "no": 0, "nobody": 0, "none": 0, "noone": 0, "nothing": 0, "other": 0, "others": 0, "our": 0, "ours": 0, "ourselves": 0, "she": 0, "some": 0, "somebody": 0, "someone": 0, "something": 0, "such": 0, "that": 0, "the": 0, "their": 0, "theirs": 0, "them": 0, "themselves": 0, "these": 0, "they": 0, "this": 0, "those": 0, "us": 0, "we": 0, "what": 0, "which": 0, "who": 0, "whom": 0, "whose": 0, "you": 0, "your": 0, "yours": 0, "yourself": 0, "yourselves": 0}
    
    def getCount(self):
        words = {}
        words.update(self.adverbs)
        words.update(self.auxillaries)
        words.update(self.prep_conj)
        words.update(self.determiners)
        return words
    
    def processWord(self, word):
        '''
        Takes a word and increases function word counter if equal to the word
        '''
        for word_list in [self.adverbs, self.auxillaries, self.prep_conj, self.determiners]:
            if word in [w for w in word_list]:
                word_list[word] += 1

    def isFunctionWord(self, word):
        '''
        Takes a word and checks if it is one of the function words. Innner state of object not influenced.
        '''
        for word_list in [self.adverbs, self.auxillaries, self.prep_conj, self.determiners]:
            if word in [w for w in word_list]:
                return True

    def processWordArray(self, text):
        '''
        Takes an array of words and counts all function words appearances
        '''
        for word in text:
            self.processWord(word)
                    
    def processSentenceWordArray(self, text):
        '''
        Takes an array of an array of words and counts all function words appearances
        '''
        for sentence in text:
                for word in sentence:
                    self.processWord(word)
                    
    def processString(self, text):
        '''
        Takes a String and counts all function words appearances
        '''
        import nltk
        words = nltk.word_tokenize(text)
        for word in words:
            self.processWord(word)

    def relativeFrequency(self, size):
        '''
        takes the absolute counts of function words and returns a normalized value by the number (size) of tokens
        '''
        return {key : (Decimal(value) / Decimal(size)) for key, value in self.getCount().iteritems()}

    def relativeFrequencyWordArray(self, words, size):
        self.processWordArray(words)
        return self.relativeFrequency(size)

    #def getVector(self, text_length):
        
    def printCount(self):
        for word_list in [self.adverbs, self.auxillaries, self.prep_conj, self.determiners]:
            print word_list
'''
Created on 23.10.2012

@author: Peter
'''
import re
import codecs
class textp(object):
    '''
    classdocs
    '''


    def __init__(self, src, limit = None):
        if(len(src) < 5 or src[(len(src) - 4):(len(src))] != ".txt"):
            raise Exception("Text file has to end in .txt and has to have a name!")
        text = ""
        for line in codecs.open(src, encoding='utf-8'):
            text += line
        self.text = self.cleanText(text)
      
    def cleanText(self, text):
        '''removing footnotes, titles, etc'''
        r = re.compile(r"<([a-z]+)>(.*?)</\1>")
        return r.sub('', text)
    
    def getText(self):
        return self.text
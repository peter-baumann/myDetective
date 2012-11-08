'''
Created on 23.10.2012

@author: Peter
'''
import re
class textp(object):
    '''
    classdocs
    '''


    def __init__(self, src, limit = None):
        if(len(src) < 5 or src[(len(src) - 4):(len(src))] != ".txt"):
            raise Exception("Text file has to end in .txt and has to have a name!")
        self.text = self.cleanText(open(src, 'r').read())
      
    def cleanText(self, text):
        '''removing footnotes, titles, etc'''
        r = re.compile(r"<([a-z]+)>(.*?)</\1>")
        return r.sub('', text)
    
    def getText(self):
        return self.text
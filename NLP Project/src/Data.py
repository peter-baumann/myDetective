'''
Created on 27.09.2012

@author: Peter
'''
#from src.parser.pdf2text import pdf2text
from p.text import textp

class Data(object):
    '''
    classdocs
    '''

    def __init__(self, src, limit = None):
        if (len(src) > 4 and src[(len(src) - 4):(len(src))] == ".txt"):
            text_parser = textp(src, limit)
            self.text = text_parser.getText()
        else:
            print "parsing error at " + src
        #elif(len(src) > 4 and src[(len(src) - 4):(len(src))] == ".pdf"):
        #    pdf_parser = pdf2text(src, limit)
        #    self.text = pdf_parser.getText()


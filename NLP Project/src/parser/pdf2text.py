'''
Created on 27.09.2012
Experimental class for PDF parsing. Only reads text from a PDF that belongs to the statistically most frequent group of font size and font
This ensures that only the main text of a document is considered and not titles or captions of images, etc.
@author: Peter
'''

import re
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter, XMLConverter
# Find the best implementation available on this platform
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class pdf2text(object):
    '''
    classdocs
    '''
    reg = re.compile('<text font="([^"]*)" bbox="([^"]*)" size="([^"]*)">([^"]*)</text>')
    
    def __init__(self, src, limit = None):
        if(len(src) < 5 or src[(len(src) - 4):(len(src))] != ".pdf"):
            raise Exception("PDF file has to end in .pdf and has to have a name!")
        input_file = open(src, "rb")
        out = StringIO()
        rsrc = PDFResourceManager()
        device = XMLConverter(rsrc, out, codec='UTF-8', laparams=None) 
        try:
            process_pdf(rsrc, device, input_file, pagenos=None, maxpages=limit, password='', check_extractable=True)
        finally:
            device.close()
            input_file.close()
        text = out.getvalue()
        out.close()
        self.text = self.cleanText(text)
        
    def getText(self):
        return self.text
    
    #Create font-size frequency list according to character counts
    def getFontSizeGroups(self, text):
        groups = {}
        for line in text.splitlines():
            m = self.reg.search(line)
            if m is not None:
                size = float(m.group(3))
                char = m.group(4)
                if len(char) != 0:
                    if size in groups:
                        if char != " ":
                            groups[size] = groups[size] + 1
                    else:
                        if char != " ":
                            groups.update({size:1})
                        else:
                            groups.update({size:0})
        groups = [[key, groups[key]] for key in sorted(groups.iterkeys(), reverse=True)]
        return groups
    
    def getMostFrequentFontSize(self, text):
        return sorted(self.getFontSizeGroups(text), key=lambda group: group[1], reverse=True)[0]
    
    #returns cleaned ASCII Text
    def cleanText(self, text):
        next_char = False
        prev_coord = []
        size = self.getMostFrequentFontSize(text)
        r_text = ""
        for line in text.splitlines():
            m = self.reg.search(line)
            if m is not None:
                if float(m.group(3)) == size[0]:
                    if next_char == True:
                        new_coord = m.group(2).split(",")
                        if abs(float(new_coord[0]) - float(prev_coord[2])) > size[0]:
                            r_text = r_text[0:len(r_text) - 1]
                        next_char = False 
                    if m.group(4) == "-":
                        prev_coord = m.group(2).split(",")
                        next_char = True
                    r_text = r_text + m.group(4)
        r_text = re.sub(r'\s{2,}', ' ', r_text.strip()).replace("\xe2\x80\x99", "'")
        return ''.join(char for char in r_text if ord(char) < 128)
    
    
    
    
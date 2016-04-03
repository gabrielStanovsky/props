import unittest
from applications.run import parseSentences
from applications.run import load_berkeley
from _jpype import shutdown
import logging


class PropsTest(unittest.TestCase):
    ''' Super class for all PropS tests '''
    
    def setUp(self):
        ''' takes care of the needed initializations '''
        logging.info("running tests")
        load_berkeley(tokenize = True)
    
    
    def getProps(self, sent):
        ''' returns the textual props representation of an input sentence '''
        g, tree = parseSentences(sent)[0]
        return str(g)
        
    def compare(self, sent, expected):
        result = self.getProps(sent)
        self.assertEqual(removeWhitespaces(result),
                         removeWhitespaces(expected), 
                         result)
                
#     def tearDown(self):
#         ''' close JVM '''
#         shutdown()
        
    
        
def removeWhitespaces(s):
    return ''.join(s.split())
        
        
        

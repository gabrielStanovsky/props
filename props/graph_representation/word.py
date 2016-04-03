import cgi
NO_INDEX = -1 # index used in cases where there's no such word in the sentence

class Word:
    """
    word container class, to add the index of the word in addition to the word 
    
    @type index: int
    @var  index: the index of the word within the sentence
    
    @type text: string
    @var  text: the text contained within this word
    """
    
    def __init__(self,index,word):
        """
        initialize a word container object
        """
        self.index = index
        self.word = word
    
    def to_conll_like(self):
        return ",".join([str(self.index),self.word])
    
    def __str__(self):
        ret = cgi.escape(self.word)
        if self.index != NO_INDEX:
            ret += '<FONT POINT-SIZE="7">[{0}]</FONT>'.format(self.index)
        return ret
    
    def __eq__(self,other_word):
        return (self.index == other_word.index) and (self.word == other_word.word)
    
    def __hash__(self):
        return self.__str__().__hash__()
    
    
    

def strip_punctuations(ls):
    """
    removes punctuations from beginning and end of the list
    """
    puncts = ':.,;\t '
    sep = "\t"
    totalElms = len(ls)
    s = sep.join([x.word for x in ls])
    ret = ls[totalElms-len(s.lstrip(puncts).split(sep)):len(s.rstrip(puncts).split(sep))]
    return ret
     


if __name__ == "__main__":
    print (Word(0,"test"))

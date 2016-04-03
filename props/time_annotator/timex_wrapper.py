from timex import ground,tag
from graph_representation.word import Word
from mx.DateTime.DateTime import gmt 


def timexWrapper(text):
    """
    wrap timex
    
    @type  text: list [word] (ordered by index)
    @param text: the text to be tagged with time expressions
    
    @rtype  tuple (list [TimeExpression], list[word])
    @return list of time expressions extracted from text and list of unmatched words 
    """
    
    text_str = " ".join([x.word for x in text])
    timeExpressions = []
    uncovered_tokens = [[x,False] for x in text]
    try:
        #timex's ground function isn't reliable
        ground_res = ground(tag(text_str),gmt())
    except:
        return ([],text)
    
    for s,val in ground_res[1]:
        textInd = text_str.find(s)
        curText = []
        numOfItems = len(s.split())
        startInd = len(text_str[:textInd].split())
        if textInd>0:
            if text_str[textInd-1] != " ":
                # deal with time expressions starting in the middle of words
                startInd-=1
        for i in range(startInd,startInd+numOfItems):
            uncovered_tokens[i][1] = True
            curText.append(text[i])
        timeExpressions.append(TimeExpression(curText,val))
    
    iterList = list(enumerate([x for x in uncovered_tokens]))
    iterList.reverse()
    for i,(x,flag) in iterList:
        if flag:
            del(uncovered_tokens[i])
        else:
            uncovered_tokens[i]=x
    
    return timeExpressions,uncovered_tokens
        


class TimeExpression:
    """
    simple record class
    """
    def __init__(self,text,value):
        self.text = text
        self.value = value
        
        
if __name__ == "__main__":
    s = "I know what you did last wednesday dad"
    text = [Word(ind,word) for ind,word in enumerate(s.split())]
    l = timexWrapper(text)

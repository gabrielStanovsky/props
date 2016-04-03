from props.dependency_tree.definitions import subject_dependencies, ARG_LABEL,\
    object_dependencies, SOURCE_LABEL, domain_label, POSSESSED_LABEL,\
    POSSESSOR_LABEL
class Proposition:
    def __init__(self,pred,args,outputType):
        self.pred = pred
        self.args = args
        self.outputType = outputType
        for ent in self.args:
            (rel,arg) = ent
            if rel == POSSESSOR_LABEL:
                ent[1] = fixPossessor(arg)
    
    def find_ent(self,ent):
        ret = []
        for i,(rel,arg) in enumerate(self.args):
            if ent in arg:
                ret.append(i)
        return ret
                 
        
    def rel_order(self,rel):
        if rel in subject_dependencies+[domain_label,POSSESSED_LABEL,POSSESSOR_LABEL]:
            return 0
        if rel == ARG_LABEL:
            return 1
        if rel in object_dependencies:
            return 2
        if rel.startswith("prep"):
            return 3
        if rel == SOURCE_LABEL:
            return 5
        else:
            return 4
        
    def __str__(self):
        PDF = (self.outputType == "pdf")
        HTML = (self.outputType == "html")
        if PDF:
            bold = lambda t:t
            color = lambda t,color:t
        if HTML:
            bold = lambda t:"<b>{0}</b>".format(t)
            color = lambda t,color:'<font color="{0}">{1}</font>'.format(color,t)
            
        curProp = r'{0}:({1})'.format(bold(self.pred),
                                      ", ".join([rel + ":" + bold(color(arg,"blue")) for rel,arg in sorted(self.args,key=lambda(rel,_):self.rel_order(rel))]))
        return curProp

mapPossessive = {"my":"I",
               "your":"you",
               "its":"it",
               "her":"she",
               "his":"he",
               "our":"we",
               "their":"they"}


def fixPossessor(possessor):
    """
    fix phrasing in a given possessor node, such as "its -> it" "her -> she" "his -> he", etc.
    """
    
    return mapPossessive.get(possessor.lower().lstrip().rstrip(),possessor)
    
#     if not (len(possessor.text) == 1): 
#         return
#     
#     curWord = possessor.text[0].word.lower()
#     possessor.text = [Word(index=possessor.text[0].index,
#                            word=mapPossessive.get(curWord, curWord))]

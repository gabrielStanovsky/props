from props.graph_representation.word import Word,NO_INDEX, strip_punctuations
import cgi
from copy import deepcopy, copy
from props.dependency_tree.definitions import time_prep, definite_label,\
    adjectival_mod_dependencies

COPULA = "SameAs"          # the textual value of a copula node
PROP = "PROP"          # the textual value of a property node
RCMOD_PROP = "PROP"    # the textual value of a property for rcmod node
POSSESSIVE = "have" # the textual value of a possessive node
APPOSITION = "appos"   # the textual value of an appositio n node
PREP = "PREP"          # the textual value of a preposition node
PREP_TYPE = "TYPE"     # the textual value of a preposition node's type
COND = "COND"          # the textual value of a conditional node
TIME = "TIME"          # the textual value of a time node
LOCATION = "LOCATION"  # the textual value of a location node
CONJUNCTION = "CONJ -" # the textual value of a conjunction node
ADVERB = "ADV"         # the textual value of a conjunction node
EXISTENSIAL = "Exists" # the textual value of a conjunction node
COND_TYPE= PREP_TYPE   # the textual value of a conditional node's type

## Node shapes
RECT_NODE_SHAPE = "rect"
DEFAULT_NODE_SHAPE = "ellipse"

PRINT_FEATURES = [("Tense",lambda t:t),
                  ("Determiner",lambda t:"det: "+t["Value"]),
                  ("Time Value",lambda t:"date: "+t),
                  ("Negation", lambda t:"negated"),
                  ("Passive Voice", lambda t:"passive"),
                  ("Modal",lambda t:"modal: "+ " ".join(t["Value"])),
                  ("Definite",lambda t:t),
                  ("Modifier",lambda t:"modifier: "+t)]

global nodeCounter
nodeCounter = 0

def resetCounter():
    global nodeCounter
    nodeCounter = 0



class Node:
    """
    node class
    
    represents a single node in the representation graph.
    @type isPredicate: bool
    @var  isPredicate: denotes if this node is a predicate
    
    @type text: list of Word object
    @var  text: the text contained within this node
    
    @type features: dict
    @var  features: syntactic features of this node (e.g., definiteness)
    
    @type propagateTo: list
    @var  propagateTo: list of Node objects onto which the properties of this node should propogate to
    
    @type span: list
    @var  span: list of indices in the original sentence which this node spans
    @todo think if this is needed, or consumed by Word
    
    @type valid: bool
    @var  valid: debug variable, indicates if this node should be converted

    @type uid: int
    @var  uid: unique id for this node, to be able to distinguish nodes with identical features
    """
    def __init__(self,text,isPredicate,features,gr,orderText = True,uid=-1):
        """
        initialize a node object
        
        @type  orderText: boolean
        @param orderText: defines if text elements should be sorted by indices upon printing in the __str__ function 
        """  
        self.isPredicate = isPredicate
        self.text = text
        self.surface_form = copy(text)
        self.features = features
        self.features["implicit"] = False
        global nodeCounter
        if uid == -1:
            self.uid  = nodeCounter
            nodeCounter +=1
        else:
            self.uid = uid
            nodeCounter = max(nodeCounter,uid)
        self.propagateTo = []
        self.orderText = orderText
        self.nodeShape = DEFAULT_NODE_SHAPE
        self.__str__() # calculate variables in str
        self.gr = gr
        gr.add_node(self)
        
    def removeLemma(self):
        if "Lemma" in self.features:
            del(self.features["Lemma"])
        
    def get_text(self,gr):
        return self.text
    
    def addPropogation(self,node):
        """
        Add a node onto which this node's properties should propogate.
        
        @type  node: Node
        @param node: The node onto which to propogate
        """
        if node not in self.propagateTo:
            self.propagateTo.append(node)
            
    def minIndex(self):
        """ 
        Minimum index covered by this node
        
        @rtype: int
        """
        if not self.surface_form:
            return NO_INDEX # TODO: why is this happenning?
        return min([w.index for w in self.surface_form])
    
    def maxIndex(self):
        """ 
        Minimum index covered by this node
        
        @rtype: int
        """
        if not self.text:
            return NO_INDEX # TODO: why is this happenning?
        return max([w.index for w in self.surface_form])
    
    def get_original_text(self):
        return " ".join([w.word for w in sorted(self.text,key=lambda w:w.index)])
    
    
    def get_sorted_text(self):
        return sorted(self.text,
                      key= lambda w:w.index)
    
    def __str__(self):
        ret = '<TABLE BORDER="0" CELLSPACING="0"><TR><TD>'
        filtered_spans = []
        for feat,_ in PRINT_FEATURES:
            if (feat in self.features) and (isinstance(self.features[feat], dict)) and ("Span" in self.features[feat]):
                filtered_spans.extend(self.features[feat]["Span"])
        
        
        if 'Lemma' in self.features and len(self.text)==1:
            self.str = [Word(index = self.text[0].index,word=self.features['Lemma'])]
        else:
            ls = self.text
            if self.orderText:
                ls = sorted(self.text,key=lambda word:word.index)
            # self.str stores the words as displayed in the node
            self.str = [w for w in ls if w.index not in filtered_spans] 
            
        self.str = strip_punctuations(self.str)
            
        ret+= "  ".join([str(x) for x in self.str])
        
        
        ret+="</TD></TR>"
        for feat, printFunc in PRINT_FEATURES:
            if feat in self.features:
                if self.isPredicate and feat =="Definite":
                    continue
                if self.features.get("Determiner",{"Value":""})["Value"] == "no":
                    del(self.features["Determiner"])
                    continue
                ret += "<TR><TD>" 
                ret+= '<FONT POINT-SIZE="10">{0}</FONT>'.format(cgi.escape(str(printFunc(self.features[feat]))))
                ret+="</TD></TR>"
            
        ret +="</TABLE>" 
        return ret
    
    
    def to_conll_like(self):
        return "\t".join([str(self.uid),
                          ";".join([w.to_conll_like() for w in self.text]),self.pos(),str(int(bool(self.isPredicate))),
                          str(int(self.features.get("top",False))),
                          ";".join([",".join([self.gr.edge_label((father,self)),str(father.uid)]) for father in self.gr.incidents(self)])
                          ])
    
    def neighbors(self):
        ret = {}
        for neighbour in self.gr.neighbors(self):
            label = self.gr.edge_label((self,neighbour))
            curEntry = ret.get(label,[])
            curEntry.append(neighbour)
            ret[label] = curEntry
        return ret
    
    def incidents(self):
        ret = {}
        for father in self.gr.incidents(self):
            label = self.gr.edge_label((father,self))
            curEntry = ret.get(label,[])
            curEntry.append(father)
            ret[label] = curEntry
        return ret
    
    
    def is_implicit(self):
        return self.features.get("implicit",False)
    
    def pos(self):
        return self.features.get("pos","")
    
    def isConj(self):
        return self.features.get("conj",False)

    def is_wh_question(self):
        """
        Returns True iff this is a WH-question word.
        From PTB pos tags, it seems that W as start of POS identifies
        such words:
        33. WDT        Wh-determiner
        34. WP         Wh-pronoun
        35. WP$        Possessive wh-pronoun
        36. WRB        Wh-adverb
        """
        return self.pos().startswith("W")


    def __hash__(self):
        return self.__str__().__hash__()
    
    def makeTopNode(self):
        if self.features.get("top",False):
            return False
        self.features["top"] = True
        return True


def getCopular(gr,index,features):
    if "Lemma" in features:
        del(features["Lemma"])
    ret = Node(text=[Word(index=index,word=COPULA)],
               isPredicate=True,
               features=features,
               gr=gr,
               orderText = True)
    ret.features["implicit"] = True
    ret.original_text=[]
    return ret

def getPossesive(gr,index):
    ret = Node(text=[Word(index=index,word=POSSESSIVE)],
               isPredicate=True,
               features={},
               gr=gr,
               orderText = True)
    ret.features["implicit"] = True
    ret.original_text=[]
    return ret
    
    

def join(node1,node2,gr):
    """
    Returns a node which is the concatenation of two nodes
    Raises in error in case they have contradicting features
    
    @type  node1: Node
    @param node1: first node to be joined
    
    @type  node2: Node
    @param node2: second node to be joined
    
    @rtype Node
    @return a node representing the union of both nodes
    """
    
    # join all values
    isPredicate = (node1.isPredicate or node2.isPredicate)
    text = list(set(node1.get_text(gr)).union(node2.get_text(gr)))
    original_text = list(set(node1.original_text).union(node2.original_text))
    surface_form = list(set(node1.surface_form).union(node2.surface_form))
    features = {}
    features.update(node1.features)
    features.update(node2.features)
    
    # remove contradicting features
    for k in set(node1.features).intersection(node2.features):
        if node1.features[k]!=node2.features[k]: 
                del(features[k])
                
    if isDefinite(node1) or isDefinite(node2):
        features["Definite"] = "definite" 
    
    # return new node
    ret = Node(isPredicate = isPredicate,
                text = text,
                features = features,
                gr = gr)
    ret.original_text = original_text
    ret.surface_form = surface_form
    return ret
    
def isDefinite(node):
    return node.features.get("Definite",False) == definite_label





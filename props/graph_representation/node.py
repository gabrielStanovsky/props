from graph_representation.word import Word,NO_INDEX, strip_punctuations
import cgi
from copy import deepcopy
from dependency_tree.definitions import time_prep, definite_label,\
    adjectival_mod_dependencies

COPULA = "SAME AS"          # the textual value of a copula node
PROP = "PROP"          # the textual value of a property node
RCMOD_PROP = "PROP"    # the textual value of a property for rcmod node
POSSESSIVE = "POSSESS" # the textual value of a possessive node
APPOSITION = "appos"   # the textual value of an appositio n node
PREP = "PREP"          # the textual value of a preposition node
PREP_TYPE = "TYPE"     # the textual value of a preposition node's type
COND = "COND"          # the textual value of a conditional node
TIME = "TIME"          # the textual value of a time node
LOCATION = "LOCATION"  # the textual value of a location node
CONJUNCTION = "CONJ -" # the textual value of a conjunction node
ADVERB = "ADV"         # the textual value of a conjunction node
EXISTENSIAL = "EXISTS" # the textual value of a conjunction node
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
                  ("Modifier",lambda t:"modifer: "+t)]

global nodeCounter
nodeCounter =0



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
    def __init__(self,isPredicate,text,features,valid,orderText = True):
        """
        initialize a node object
        
        @type  orderText: boolean
        @param orderText: defines if text elements should be sorted by indices upon printing in the __str__ function 
        """  
        self.isPredicate = isPredicate
        self.text = text
        self.features = features
        self.valid = valid
        global nodeCounter
        self.uid  = nodeCounter
        nodeCounter +=1
        self.propagateTo = []
        self.orderText = orderText
        self.nodeShape = DEFAULT_NODE_SHAPE
        self.__str__() # calculate variables in str
        
    def get_text(self,gr):
        return self.text
        
    def copy(self):
        """ 
        'copy constructor' 
        """
        
        # get proper type and new uid
        ret = self.__class__(isPredicate = self.isPredicate,
                             text = self.text,
                             features = self.features,
                             valid = self.valid)
        
        # copy propagations
        for curNode in self.propagateTo:
            addSymmetricPropogation(ret, curNode)
            
        return ret
    
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
        if not self.text:
            return NO_INDEX # TODO: why is this happenning?
        return min([w.index for w in self.text])
    
    def maxIndex(self):
        """ 
        Minimum index covered by this node
        
        @rtype: int
        """
        if not self.text:
            return NO_INDEX # TODO: why is this happenning?
        return max([w.index for w in self.text])
        
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
                ret += "<TR><TD>" 
                ret+= '<FONT POINT-SIZE="10">{0}</FONT>'.format(cgi.escape(str(printFunc(self.features[feat]))))
                ret+="</TD></TR>"
            
        ret +="</TABLE>" 
        return ret
    
    def __hash__(self):
        return self.__str__().__hash__()

class CopularNode(Node):
    """
    A class representing a copular head "BE" node.
    """
    @classmethod
    def init(cls,index,features,valid):
        if "Lemma" in features:
            del(features["Lemma"])
        return cls(isPredicate=True,
                   text=[Word(index,COPULA)],
                   features=features,
                   valid=valid)
                      

class PossessiveNode(Node):
    """
    A class representing a copular head "HAS" node.
    """
    @classmethod
    def init(cls,index,features,valid):
        return cls(isPredicate=True,
                   text=[Word(index,POSSESSIVE)],
                   features=features,
                   valid=valid)
                      
class PropNode(Node):
    """
    A class representing a prop head node
    """
    @classmethod
    def init(cls,features,valid,index,parent_relation):
        if "Lemma" in features:
            del(features["Lemma"])
        ret =  cls(isPredicate=True,
                   text=[Word(index,PROP)],
                   features=features,
                   valid=valid)
        ret.parent_relation = parent_relation
        return ret
    
    def copy(self):
        ret = Node.copy(self)
        ret.parent_relation = self.parent_relation
        if hasattr(self, 'str'):
            ret.str = self.str
        return ret
    
    def is_relative(self):
        if "relative" not in self.features:
            return False
        return self.features["relative"]
    
    def is_prenominal(self):
        # TODO: this should be a property of the edge and not the node
        return (self.parent_relation == "amod")
    
    def get_text(self,gr):
        return []
                      

class RCMODPropNode(Node):
    """
    A class representing a prop head for rcmod node
    """
    @classmethod
    def init(cls,features,valid):
        return cls(isPredicate=True,
                      text=[Word(NO_INDEX,RCMOD_PROP)],
                      features=features,
                      valid=valid)
    def is_prenominal(self):
        return False





class TimeNode(Node):
    """
    A class representing a time head node
    """
    @classmethod
    def init(cls,features):
        return cls(isPredicate=False,
                      text=[Word(NO_INDEX,TIME)],
                      features=features,
                      valid=True)
        cls.nodeShape = RECT_NODE_SHAPE
    
    def get_text(self,gr):
        neighbors = gr.neighbors(self)
        ret = []
        for n in neighbors:
            ret.extend(n.get_text(gr))
        return sorted(ret,key=lambda x:x.index)
            
class LocationNode(Node):
    """
    A class representing a location head node
    """
    @classmethod
    def init(cls,features):
        return cls(isPredicate=True,
                      text=[Word(NO_INDEX,LOCATION)],
                      features=features,
                      valid=True)
    
    def get_text(self,gr):
        neighbors = gr.neighbors(self)
        ret = []
        for n in neighbors:
            ret.extend(n.get_text(gr))
        return sorted(ret,key=lambda x:x.index)

class PrepNode(Node):
    """
    A class representing a preposition head node
    """
    @classmethod
    def init(cls,index,prepType,features,valid):
        prepType = prepType.lower()
        ret = cls(isPredicate=True,
                      text=[Word(index,"{0}-{1}".format(PREP,prepType))],
                      features=features,
                      valid=valid) 
        ret.prepType = prepType
        return ret
        
        
    def copy(self):
        ret = Node.copy(self)
        ret.prepType = self.prepType
        if hasattr(self, 'str'):
            ret.str = self.str
        return ret
    
    def get_text(self,gr):
        return [Word(index = self.text[0].index,
                    word = self.prepType)]
    
    def is_time_prep(self):
        return self.prepType in time_prep


class CondNode(Node):
    """
    A class representing a conditional/temporal head node
    """
    @classmethod
    def init(cls,index,condType,features,valid):
        condType = condType.lower()        
        ret= cls(isPredicate=True,
                      text=[Word(index,"{0}-{1}".format(COND,condType))],
                      features=features,
                      valid=valid)
        ret.condType = condType
        ret.nodeShape = RECT_NODE_SHAPE
        return ret
    
    def get_text(self,gr):
        return [Word(index = self.text[0].index,
                    word = self.condType)]
        
    def copy(self):
        ret = Node.copy(self)
        ret.condType = self.condType
        return ret



class AppositionNode(Node):
    """
    A class representing an apposition head node
    """
    @classmethod
    def init(cls,index,features):
        return cls(isPredicate=False,
                      text=[Word(index,APPOSITION)],
                      features=features,
                      valid=False)



class ConjunctionNode(Node):
    """
    A class representing an conjunction head node
    """
    @classmethod
    def init(cls,text,features):
        """
        initialize a conjunction head node
        """
        conjType = " ".join([x.word for x in sorted(text,
                                               key=lambda word:word.index)])
        
        text = [Word(NO_INDEX,CONJUNCTION)] + text
        ret =  cls(isPredicate=True,
                      text=text,
                      features=features,
                      valid=True)
        ret.conjType = conjType
        ret.__str__()
        return ret
    
    def copy(self):
        ret = Node.copy(self)
        ret.conjType = self.conjType
        return ret
    
    def get_text(self,gr):
        neighbors = gr.neighbors(self)
        ret = []
        for n in neighbors:
            ret.extend(n.get_text(gr))
        return sorted(ret,key=lambda x:x.index)

    

class advNode(Node):
    """
    A class representing an adverb head node
    """
    @classmethod
    def init(cls,features):
        """
        initialize an adverb head node
        """
        return cls(isPredicate=True,
                      text=[Word(NO_INDEX,ADVERB)],
                      features=features,
                      valid=True)


        
def isCopular(node):
    """
    check if this node is an copular instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is an copular instance
    """
    return isinstance(node,CopularNode)


def isApposition(node):
    """
    check if this node is an apposition instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is an apposition instance
    """
    return isinstance(node,AppositionNode)

def isProp(node):
    """
    check if this node is a prop instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is prop node instance
    """
    #TODO: efficiency
    return isinstance(node,PropNode)


def isRcmodProp(node):
    """
    check if this node is a prop instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is prop node instance
    """
    #TODO: efficiency
    return isinstance(node,RCMODPropNode)


def isConjunction(node):
    """
    check if this node is a conjunction instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is conjunction node instance
    """
    #TODO: efficiency
    return isinstance(node,ConjunctionNode)


def isPreposition(node):
    """
    check if this node is a preposition instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is preposition node instance
    """
    #TODO: efficiency
    return isinstance(node,PrepNode)


def isTime(node):
    """
    check if this node is a time instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is time node instance
    """
    #TODO: efficiency
    return isinstance(node,TimeNode)

def isLocation(node):
    """
    check if this node is a location instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is location node instance
    """
    #TODO: efficiency
    return isinstance(node,LocationNode)



def isAdverb(node):
    """
    check if this node is a adverb instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is adverb node instance
    """
    #TODO: efficiency
    return isinstance(node,advNode)


def isCondition(node):
    """
    check if this node is a Cond instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is condition node instance
    """
    #TODO: efficiency
    return isinstance(node,CondNode)

def isDefinite(node):
    return node.features.get("Definite",False) == definite_label

def isNominal(node,gr):
    if node.isPredicate: #predicate
        return False
    if [father for father in gr.incidents(node) if isProp(father)]: #prop
        return False
    return True
    


def isPossessive(node):
    """
    check if this node is a Possessive instance
    
    @type  node: Node
    @param node: node to examine
    
    @rtype  bool
    @return True iff this node is possessive node instance
    """
    #TODO: efficiency
    return isinstance(node,PossessiveNode)




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
    
    # make sure everything is ok
    if node1.isPredicate != node2.isPredicate:
        #raise Exception("Contradicting isPredicate value")
        print "Contradicting isPredicate value"
                
    if (not node1.valid) or (not node2.valid):
        raise Exception("Invalid node cannot be joined")
    
    
    # join all values
    isPredicate = (node1.isPredicate and node2.isPredicate)
    text = list(set(node1.get_text(gr)).union(node2.get_text(gr)))
    features = {}
    features.update(node1.features)
    features.update(node2.features)
    valid = node1.valid
    
    # remove contradicting features
    for k in set(node1.features).intersection(node2.features):
        if node1.features[k]!=node2.features[k]: 
                del(features[k])
                print("Contradicting features")
                
    
    # return new node
    return Node(isPredicate = isPredicate,
                text = text,
                features = features,
                valid = valid)


def addSymmetricPropogation(node1,node2):
    """
    Add two nodes onto each other's propogation
    
    @type  node1: Node
    @param node: The node onto which to propogate node2
    
    @type  node1: Node2
    @param node: The node onto which to propogate node1
    """
    
    node1.addPropogation(node2)
    node2.addPropogation(node1)


if __name__ == "__main__":
    copNode = CopularNode(index = 1,
                          features={"tense":"past"},
                          valid=True)
    n = copNode.copy()
    

from __builtin__ import dir
from graph_representation.graphParsingException import GraphParsingException
from nltk.tree import Tree
from graph_representation.word import Word
#from graph_representation.graph_utils import find_tree_matches
__author__ = 'jessica'

from dependency_tree.definitions import *
from constituency_tree.definitions import *
from constituency_tree.my_definitions import any_in
import copy,os
from Tense import tense_rules
UNDERSCORE = "_"





HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR", ".")
# intransitive_verbs = []
# fin = open(HOME_DIR+"intransitive_verbs.txt")
# for line in fin:
#     w = line.strip()
#     if w:
#         intransitive_verbs.append(w)
# fin.close()

# DepTree is a class representing a dependency tree
class DepTree(object):

    def __init__(self,pos,word,id,parent=None,parent_id = None,parent_relation=None,children=[],wsj_id = 0, sent_id = 0):
        self.children = children                             # List of node's children
        self.parent = parent                                  # Node's parent
        self.parent_relation = parent_relation          # Node's parent relation
        self.parent_id = parent_id                          # Node's parent id
        self.pos = pos                                          # pos tag
        self.word = word                                        # word from sentence
        self.id = int(id)                                      # location in sentence
        self.function_tag = []                                # function tag as it in constituency tree
        self.is_head_of_time_expression = 0                 # indicates if the node is a head of time expression
        self.constituent = 0
        self.wsj_id = wsj_id
        self.sent_id = sent_id
        self.is_nominal = False
        self.nominal_argument = None
        self.childDic = []



    def set_parent(self, new_parent): self.parent = new_parent
    def set_parent_id(self,parent_id): self.parent_id = parent_id
    def get_parent(self): return self.parent
    def get_word(self): return self.word
    def get_pos(self): return self.pos
    def add_child(self,child): self.children.append(child)
    def get_children(self): return self.children
    def get_parent_relation(self): return self.parent_relation
    def is_head_of_time_expression(self): return self.is_head_of_time_expression
    def get_children_relations(self): return [c.parent_relation for c in self.children]

    def __str__(self):
        if not self.children : return ""
        str = ""
        for child in self.children:
            str += "%s(%s,%s)\n%s" % (child.get_parent_relation(), self.word,child.get_word() ,child)
        return str

    def longest_path(self):
        if not self.children:
            return [self.parent_relation]
        maxPath=[]
        for c in self.children:
            cur = c.longest_path()
            if (len(cur) >len(maxPath)):
                maxPath = cur
        return [self.parent_relation]+maxPath
    
    
    def match(self,pat):
        if not self.childDic:
            self.childDic = self._get_child_dic()    
        # check if there're enough children to satisfy pattern
        if len(self.children) < len(pat):
            return False
        #check if current head matches the head of the pattern
        if not eval(pat.node):
            return False
        #mark head as matching pattern's head
        ret = [self]
        
        # find a child matching each of the pattern's children
        availableChildren = [(i,c) for i,c in enumerate(self.children)]
        lastMatch = -1
        for c_pat in pat:
            for i,c_t in availableChildren:
                successor = False
                if c_pat.node.startswith("$+"):
                    successor = True
                    c_pat.node = c_pat.node[2:]
                curMatch = c_t.match(c_pat)
                if curMatch:
                    if successor:
                        if i-lastMatch != 1:
                            return False
                    lastMatch = i
                    ret.append(curMatch)
                    availableChildren.remove((i,c_t))
                    break
            if not curMatch: 
                return False
        return ret
    
    
    def get_text(self):
        ret = [Word(index=self.id,word=self.word)]
        for c in self.children:
            ret += c.get_text()
        return ret
        
                

  # get the original sentence from the PTB
    def get_original_sentence(self, root=True):
        if root:
            subtree = self.children[0]._get_subtree()
        else:
            subtree = self._get_subtree()
        return " ".join(subtree[x] for x in sorted(subtree))

    # return rooted subtree word dictionary by self.id
    def _get_subtree(self,filterFunc=lambda x:True):
        if filterFunc(self):
            ret = {self.id:self.word}
        else:
            ret = {}
        if not self.children: 
            return ret
        for child in self.children:
            ret.update(child._get_subtree(filterFunc))
        return ret
    
    # get a dictionary of [list] of children by their parent relation (if there's several)
    def _get_child_dic(self):
        d = {}
        for c in self.children:
            if c.parent_relation not in d:
                d[c.parent_relation] = []
            d[c.parent_relation].append(c)
        return d
        

    # return rooted subtree word dictionary by self.id
    def _get_subtree_nodes(self,includeHead = False):
        def inner(node):
            ret = {node.id:node}
            for child in node.children:
                ret.update(inner(child))
            return ret
        d = inner(self)
        if not includeHead: d.pop(self.id)
        return d

    # return True if the node is a predicate - deprecated
    def is_predicate(self):
        if self.is_verbal_predicate():
            return True
        return False
    
    # returns [self] if the node is an possesive predicate
    def is_possesive_predicate(self):
        possChildList = any_in([c.parent_relation for c in self.children], [POSS_LABEL])
        ret = []
        # for each possessive create a different predicate
        for poss in possChildList:
            #poss child holds the index of the possesor
            if self.children[poss].is_determined():
                self.possChild = [poss]
                ret.append(copy.copy(self))
                self.adjectivalChild=[]
            
        return ret

    def is_nominal_predicate(self):
        if self.is_nominal:
            return [self]
        return []

    
    # returns [self] if the node is an copular predicate
    def is_copular_predicate(self):
        if (self.word.lower() in copular_verbs) and (self.is_verbal_predicate()):
            self.copSubj = any_in([c.parent_relation for c in self.children],subject_dependencies)
    
            if self.copSubj:
                if len(self.copSubj) !=1:
#TODO                    print "subj - " + self.get_original_sentence(False)
                    return []
                self.copObj = any_in([c.parent_relation for c in self.children],clausal_complements)
                if len(self.copObj) !=1:
#TODO                    print "obj - " + self.get_original_sentence(False)
                    return []
            #print " , ".join([c.parent_relation for c in self.children])
                return [self]
        return []
    
    
    
    
    def _COPULAR_PREDICATE_FEATURE_Longest_Path(self):
        return {"Value":self.longest_path(),
               "Span":[self.id]}

    # get the copular predicate
    def _COPULAR_PREDICATE_FEATURE_Copular_Predicate(self):
        assert(len(self.copSubj)==1)
        copSubjChild = self.children[self.copSubj[0]]
        d = copSubjChild._get_subtree_nodes(includeHead = False)
        ret = {"Value":copSubjChild,
               "Span":d.keys()}
        return ret
    
    # get the copular predicate
    def _COPULAR_PREDICATE_FEATURE_Copular_Object(self):
        assert(len(self.copObj)==1)
        copObjChild = self.children[self.copObj[0]]
        d = copObjChild._get_subtree_nodes(includeHead = False)
        ret = {"Value":copObjChild,
               "Span":d.keys()}
        return ret
       
    def _COPULAR_PREDICATE_FEATURE_Propogation(self):
        """
        X is <adj> Y => <adj> X
        """
        copSubjChild = self.children[self.copSubj[0]].get_original_sentence(False)
        copObjChild = self.children[self.copObj[0]]
        ts = copObjChild.is_adjectival_predicate() 
        if ts:
            val = ""
            for t in ts:
                if not t.relative_adj:
                    copAdj = t._ADJECTIVAL_PREDICATE_FEATURE_Adjective()["Value"].get_original_sentence(False)
                    val += "({0},{1})".format(copAdj,copSubjChild)
            return {"Value":val,
                    "Span":self.id}
        else:
            return False,False
        
        
    

    # returns [self] if the node is a verbal predicate : (1) verb POS tag (2) not auxiliary verb
    def is_verbal_predicate(self):
        child_dic = self._get_child_dic()
        if self.parent_relation in aux_cop_dependencies:
            return []
        if self.pos in VERB_POS:
            return [self]
        if (self.pos == VBG) and any_in(child_dic.keys(),arguments_dependencies):
            return [self]
        return []
    
    
    
    # returns [self] if the node is an adjectival predicate
    def is_adjectival_predicate(self):
        self.adjectivalChildren = [c for c in self.children if (c.parent_relation in adjectival_mod_dependencies)]
        ret = []
        # if this item is determined
        # for each adjective create a different predicate
        for adj in self.adjectivalChildren:
            if (adj.pos in relative_adj_pos) or (adj.word.lower() in relative_adj_words):
                self.relative_adj = True
            else:
                self.relative_adj = False
            self.adjectivalChild = [adj]
            ret.append(copy.copy(self))
            self.adjectivalChild=[]
        self.adjectivalChildList = ret
        return ret
    
    
        # get the adjective predicate
    def _ADJECTIVAL_PREDICATE_FEATURE_Adjective(self):
        #childrenCopy = [x for x in self.children]
        assert (len(self.adjectivalChild) < 2)
        adjChild = self.adjectivalChild[0]
        #self.children = self.adjectivalChild
        d = adjChild._get_subtree_nodes(includeHead = False)
        ret = {"Value":adjChild,#adjChild.get_original_sentence(False),
               "Span":d.keys()}
        #self.children = childrenCopy
        return ret
    
    # get the adjective predicate
    def _ADJECTIVAL_PREDICATE_FEATURE_Subject(self):
        childrenCopy = [x for x in self.children]
        self.children = [x for x in self.children if x not in self.adjectivalChildren]
        d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),#self.get_original_sentence(False),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret
    
    def is_relative_clause(self):
        self.rcChildIndList = any_in([c.parent_relation for c in self.children], relclause_dependencies)
        ret = []
        
        for c in self.rcChildIndList:    
            self.rcChildIndex = c
            self.rcChild = self.children[c]
            
            # find markers
            inds = any_in([x.word.strip() for x in self.rcChild.children],
                          relclause_markers)
            
            # if there is a marker, check if it has a suitable relation
            self.possRels = [(x,self.rcChild.children[x].parent_relation) for x in inds 
                        if self.rcChild.children[x].parent_relation in object_dependencies + subject_dependencies]
            
            if self.possRels:
                assert len(self.possRels)==1
                self.rcmodRel = self.possRels[0][1]
                #remove the marker from tree
                del(self.rcChild.children[self.possRels[0][0]])
                
            # else - find what of (subj, dobj, iobj) doesn't exist
            else:
                rels = [x.parent_relation for x in self.rcChild.children]
                if not any_in(rels,subject_dependencies):
                    self.rcmodRel = SUBJ_LABEL
                elif not ((DIRECT_OBJECT_LABEL in rels) or (OBJECT_LABEL in rels)):
                    self.rcmodRel = DIRECT_OBJECT_LABEL
                else:
                    self.rcmodRel = INDIRECT_OBJECT_LABEL
            
            self.rcType = self.rcChild.parent_relation
            ret.append(copy.copy(self))
        self.rcmodPred = ret
        return ret
                
    def _RELCLAUSE_PREDICATE_FEATURE_Prop(self):
        subj,obj = [""]*2
        pred = self.rcChild.word
        
        if self.rcmodRel in subject_dependencies:
            subj = self.word
            dobjs = any_in([x.parent_relation for x in self.rcChild.children],[DIRECT_OBJECT_LABEL])
            if dobjs:
                obj = self.rcChild.children[dobjs[0]].get_original_sentence(False)
            else:
                objs = any_in([x.parent_relation for x in self.rcChild.children],[OBJECT_LABEL])
                if objs:
                    obj = self.rcChild.children[objs[0]].get_original_sentence(False)
                else:
                    objs = any_in([x.parent_relation for x in self.rcChild.children],object_dependencies)
                    if objs:
                        obj = self.rcChild.children[objs[0]].get_original_sentence(False)
                
        elif self.rcmodRel in object_dependencies:
            obj = self.word
            subjs = any_in([x.parent_relation for x in self.rcChild.children],subject_dependencies)
            if subjs:
                subj = self.rcChild.children[subjs[0]].get_original_sentence(False)
        
        return {"Value":"{0}:({1},{2})".format(pred,subj,obj),
                "Span":[self.id]}
    
    
    def _RELCLAUSE_PREDICATE_FEATURE_Type(self):
        return {"Value":self.rcType,
                "Span":self.rcChild.id}
    
    def _RELCLAUSE_PREDICATE_FEATURE_Relclause(self):
        d = self.rcChild._get_subtree_nodes(includeHead = True)
        ret = {"Value":self.rcChild,
               "Span":d.keys()}
        return ret
    
    
    # an alternative version of the tree, where the relative clause is lifted, and its father node is his subject 
    def __RELCLAUSE_PREDICATE_FEATURE_Lift(self):
        selfCopy = copy.copy(self)
        # remove the rc child 
        selfCopy.children = [x for x in self.children if x.parent_relation not in relclause_dependencies]
        # plant the father under the rc child with subject relation
        self.rcChild.add_child(selfCopy)
        selfCopy.parent_relation = self.rcmodRel       
        
        d = self.rcChild._get_subtree_nodes(includeHead = True)
  
        ret = {"Value":True,
               "Span":d.keys()}
        return ret
    
    def _RELCLAUSE_PREDICATE_FEATURE_Rest(self):
        childrenCopy = [x for x in self.children]
        self.children = [x for i,x in enumerate(self.children) if i not in self.rcChildIndList]
        d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret
    
    def is_conditional_predicate(self):
        self.condPred = []
        self.markChildren = [] 
        for childInd,child in enumerate(self.children):
            if child.parent_relation in clausal_modifiers_labels:
                self.condRel = []
                markChildList = [x for x in any_in([c.parent_relation for c in child.children], ["mark"])
                                 if len(child.children[x].children)==0]
                if not markChildList:
                    markChildList = [x for x in any_in([c.parent_relation for c in child.children], ["advmod"])
                                     if len(child.children[x].children)==0]
                if len(markChildList)>0:
                    # return the parent of this node, and mark the way to the mark child
                    self.markChildNode = child
                    self.markChildren.append(childInd)
                    for markChildInd in sorted(markChildList,reverse=True): # append all marks - Assuming this is a dep limitation, see sentence 129 ("so that")
                        curChild = child.children[markChildInd]
                        self.condRel = [curChild] + self.condRel
                        child.children.remove(curChild)
                                                
                    self.condPred.append(copy.copy(self)) 
    #             elif len(markChildList)>1:
    #                 raise GraphParsingException("No handling for more that one mark ")
        return self.condPred
    
    def _CONDITIONAL_PREDICATE_FEATURE_Condition(self):
        #in case of "if" the condition is the subtree of this node, excluding the mark child - "if" 
        #if (self.cond_rel in [COND_IF,COND_AFTER]):
        d = self.markChildNode._get_subtree_nodes(includeHead = True)
        ret = {"Value":self.markChildNode,#self.markChildNode.get_original_sentence(False),
               "Span":d.keys()}
        return ret
        #else
        #return False,False
    
    def _CONDITIONAL_PREDICATE_FEATURE_Outcome(self):
        #in case of "if" the outcome is the parent subtree of this node, excluding this child
#        if (self.cond_rel in [COND_IF,COND_AFTER]):
        childrenCopy = [x for x in self.children]
        self.children = [x for i,x in enumerate(self.children) if i not in self.markChildren]
        d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),#self.get_original_sentence(False),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret
        #else
        #return False,False
    
    def _CONDITIONAL_PREDICATE_FEATURE_Mark(self):
        return {"Value" : " ".join([c.word for c in sorted(self.condRel,key=lambda x:x.id)]),
                "Span":[min([c.id for c in self.condRel])]} #TODO: efficiency
        
    
    # returns [self] if the node is an appositional predicate
    def is_appositional_predicate(self):
        self.apposChild = [c for c in self.children if (c.parent_relation in appositional_dependencies)]
#        if (not(len(self.apposChild) <2)):
#TODO            print self.get_original_sentence(False)
        if self.apposChild:
            return [self]
        
        return []
    
    def is_determined(self):
        return True
        #return (self.pos in determined_labels)

    # returns  list of the verbal predicates in subtree
    def collect_verbal_predicates(self):
        if self.is_verbal_predicate():
            yield self
        for child in self.children:
            for node in child.collect_verbal_predicates():
                yield node


    def nodes(self):
        yield self
        for child in self.children:
            for node in child.nodes():
                yield node

    
    
    def collect_predicates(self,funcs):
        ret = [f(self) for f in funcs]
        for child in self.children:
            childRet = child.collect_predicates(funcs)
            for i,x in enumerate(ret):
                x.extend(childRet[i])
        return ret
                
        

    def is_argument(self):
        if (self.get_parent_relation() in arguments_dependencies):
            return True
        # "to Y" is considered an argument in cases such as "X ->(prep) TO -> Y"
        #if (self.pos == TO) and (self.get_parent_relation() in prepositions_dependencies):
        #    return True
        return False

    #returns a list of arguments in the subtree
    def collect_arguments(self):
        return [c for c in self.children if c.is_argument()]

    # return the original Stanford textual format representing this subtree
    def to_original_format_for_json(self,root=False):
        #artificially changing the parent of this subtree to zero
        if root:
            parent_id = 0
        else:
            parent_id = self.parent_id
        ret = [(self.id,"    ".join([str(x) for x in [self.id,self.word,UNDERSCORE,self.pos,self.pos,UNDERSCORE,parent_id,self.parent_relation,UNDERSCORE,UNDERSCORE]]))]
        for child in self.children:
            ret += child.to_original_format_for_json()
        return  sorted(ret)

    # return the original Stanford textual format representing this subtree
    def to_original_format(self,root=False):
        def inner(depTree):
            #artificially changing the parent of this subtree to zero
            if root:
                parent_id = 0
            else:
                parent_id = depTree.parent_id

            ret = [(depTree.id,"\t".join([str(x) for x in [depTree.id,depTree.word,UNDERSCORE,depTree.pos,depTree.pos,UNDERSCORE,parent_id,depTree.parent_relation,UNDERSCORE,UNDERSCORE]])+"\n")]

            for child in depTree.children:
                ret.extend(inner(child))
            return ret

        ls = inner(self)
        ret = ""
        for x in sorted(ls,key=lambda x:x[0]):
            ret+=x[1]
        return ret

    #draw this tree (using nltk)
    def draw(self):
        self._to_nltk_format().draw()


    #return an nltk tree format of this tree
    def _to_nltk_format(self):
        from nltk import Tree
        
        return Tree(self.parent_relation,
                   [Tree(self.pos,
                         [self.word] + [c._to_nltk_format() for c in self.children]  )])
                
#         from nltk import Tree
#         label = "({0}) {1} ({2})".format(self.parent_relation,self.word,self.pos)
#         if not self.children:
#             return label
#         return Tree(label,[c._to_nltk_format() for c in self.children])


    # Feature functions, should conform to naming _(PREDICATE/ARGUMENT)_FEATURE_(feature_name)
    # and return a tuple of (value,span)

    #return the head of the
    def _VERBAL_PREDICATE_SUBTREE_Head(self):
        word = self.word
        self.head_span = [self.id]
        for child in self.children:
            if child.get_parent_relation() == prt_dependency:
                word = self.word + " " + child.word
                self.head_span = [self.id, child.id]
                break
        return  {"Value":word,
                "Span":self.head_span,
                "Extra":"%s,%s" % (self.word,self.get_parent_relation())}
        
        
    def _VERBAL_PREDICATE_FEATURE_Definite(self):
        if self.pos in determined_labels:
            return definite_label
#REMOVED CODE FOR LOOKING AT DETERMINERS - 
        det = self._VERBAL_PREDICATE_FEATURE_Determiner()
        if isinstance(det,dict) and "Value" in det: 
            if det["Value"].lower() in definite_determiners:
                return definite_label
        return indefinite_label
    
    def is_definite(self):
        return self._VERBAL_PREDICATE_FEATURE_Definite() == definite_label

        
    #feature extraction for negation
    def _VERBAL_PREDICATE_FEATURE_Negation(self):
        #span of the tokens involved - initialized to false
        span=0
        # check if one of dependents causes the negation of this predicate
        negating_nodes = filter(lambda x:x.get_parent_relation() in negation_dependencies, self.children)
        if not negating_nodes:
            negating_nodes = [c for c in self.children if
                              c.word in negating_words and len(c.children)==0]
        if negating_nodes:
            child = negating_nodes[0]
            span = [child.id]
            return  {"Value":True,
                "Span":span}
        
        return (False,False)
    
    #feature extraction for determiner
    def _VERBAL_PREDICATE_FEATURE_Determiner(self):
        #span of the tokens involved - initialized to false
        span=0
        # check if one of dependents causes the negation of this predicate
        det_nodes = filter(lambda x:x.get_parent_relation() in determiner_dependencies, self.children)
        if det_nodes:
            span = [child.id for child in det_nodes]
            return  {"Value":" ".join([child.word for child in 
                                       sorted(det_nodes,key=lambda x:x.id)]),
                     "Span":span}
                #"Extra":"%s,%s" % (child.word,child.get_parent_relation())}
        #else
        return (False,False)
    
    
    def _VERBAL_PREDICATE_FEATURE_Modal(self):
        childDic = self._get_child_dic()
        modal_children = []
        for aux in aux_dependencies:
            modal_children.extend(childDic.get(aux,[]))
        ret = [c.word for c in modal_children if c.word in modal_list]
        if not ret:
            return False
        else:
            return {"Value":ret}
    
    # If the node is a predicate and its voice is passive - returns True
    # Notice that the behaviour for node that is not a predicate is unexpected
    def _VERBAL_PREDICATE_FEATURE_Passive_Voice(self):
        #span of the tokens involved - initialized to false
        span=0
        # check if one of dependents causes the negation of this predicate
        passive_nodes = filter(lambda x:x.get_parent_relation() in passive_dependencies, self.children)
        if passive_nodes:
            #child = passive_nodes[0]
            ids = [x.id for x in passive_nodes]
            if len(ids) == 1:
                span = ids[0]
            else:
                span = (min(ids),max(ids))
            
            return  {"Value":True}
                #"Span":span}
            # "Extra":"%s,%s" % (child.word,child.get_parent_relation())}
        #else
        return (False,span)


    # catch all feature, for now theres no parsing of arguments
    def _DONT_VERBAL_ARGUMENT_FEATURE_All_Text(self):
        dic = self._get_subtree()
        return (True, dic.keys())

    #returns the number of nodes in this subtree
    def size(self):
        return 1+reduce(lambda x,y:x+y,[c.size() for c in self.children],0)

    # filter node's children according to the given function
    # returns (True/False, span) : True/False indicates if the node has children after the filter.
    #                              span indicates the filtered children min and max indexes
    def _get_span_of_filtered_children(self, child_func):
        nodes = filter(lambda x:child_func(x), self.children)
        if nodes == []:
            return False,(-1,-1), None
        ids = [x.id for x in nodes]
        min_id,max_id = (min(ids),max(ids))
        return  True,(min_id,max_id), nodes[0]


    # returns the tense of a predicate : past, present, future, unknown
    def _VERBAL_PREDICATE_FEATURE_Tense(self):
        tense_result = tense_rules.get_tense(self)[0]
        if tense_result == "unknown":
            return False 
        return tense_result 




    # returns the span of the subtree rooted in current node
    def get_span_of_subtree(self):
        d = self._get_subtree()
        return (min(d),max(d))


    #feature extraction for time
    def _VERBAL_PREDICATE_SUBTREE_Time(self):
        #span of the tokens involved - initialized to false
        span=0
        
        # check if one of dependents indicates time of this predicate
        time_nodes = filter(lambda x:x.get_parent_relation() in time_dependencies, self.children)
        if time_nodes:
            span_list = []
            for time_node in time_nodes:
                value = time_node
                min_index, max_index = time_node.get_span_of_subtree()
                span_list += range(min_index,max_index+1)
            span_list.sort()
            return (value,span_list)
        return (False,span)

    def _DONT_RUN_VERBAL_PREDICATE_FEATURE_Dep_Tree(self):
        return (self.to_original_format_for_json(),False)

    def _VERBAL_PREDICATE_FEATURE_Lemma(self):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr = WordNetLemmatizer()
        if self.pos in pos_penn_to_wordnet:
            return lmtzr.lemmatize(self.word, pos_penn_to_wordnet[self.pos])
        else:
            return False

    # TODO functions:

    def _DONT_RUN_VERBAL_PREDICATE_FEATURE_TODO_prep_as(self):

        relevant_children = filter(prep_as_child_func,self.children)
        if not relevant_children:
            return False,False
        if (len(relevant_children) !=1):
            print self.get_original_sentence(root=False)
        child = relevant_children[0]
        d = child._get_subtree_nodes(includeHead = True)
        return  {"Value":child.get_original_sentence(root=False),
                "Span":(min(d),max(d)),
                "Extra":"(%s,%s)" % (child.word,child.get_parent_relation())}


    def report(self):
        return "{0}_{1}".format(self.wsj_id,self.sent_id)

    def is_prepositional_predicate(self):
        self.prepChildIndList = any_in([c.parent_relation for c in self.children], prepositions_dependencies)
        self.prepChildIndList.extend([i for i in range(len(self.children))
                                      if (self.children[i].pos == 'TO') and  (self.children[i].parent_relation == 'dep')])
        ret = []
        
        for prep in self.prepChildIndList:     
            self.prepChildInd = prep
            prepChild = self.children[self.prepChildInd]
            childDic = prepChild._get_child_dic()
            extraChildren = childDic.get('advmod',[]) + childDic.get('mwe',[]) 
            self.prepType = " ".join([c.word for c in sorted([prepChild] + extraChildren,key=lambda c:c.id)])
            self.prepInd = prepChild.id
            #children_copy = [c for c in prepChild.children]
            prepChild.children = [c for c in prepChild.children if c not in extraChildren]
            ret.append(copy.copy(self))
            #prepChild.children = children_copy
            self.prepChildInd=[]
            
        self.prepChildList = ret
        return ret
    
    def unhandled_advcl(self):
        self.advcl,other = double_filter(lambda c:c.parent_relation == "advcl", self.children)
        if not self.advcl:
            return False
        self.children = other
        return True

    def is_clausal_complement(self):
        compChildIndList = any_in([c.parent_relation for c in self.children], clausal_complements)
        d1 = self._get_child_dic()
        if self.parent_relation == 'ccomp':
            for c1 in d1.get('advcl',[]):
                d2 = c1._get_child_dic()
                if MARK_LABEL not in d2:
                    compChildIndList.append(self.children.index(c1))
            
            
        if not compChildIndList:
            return False
        self.compChildList = [self.children[ind] for ind in compChildIndList]
        children_copy = [c for c in self.children]
        self.children = [children_copy[i] for i in range(len(self.children)) 
                         if i not in compChildIndList]
        self.compSubj = copy.copy(self)
        self.children = children_copy
        return True
        
        

    
#     def is_existensial_predicate(self):
#         childDic = self._get_child_dic()
#         if EXPL_LABEL in childDic:
#             self.explSubj = any_in([c.parent_relation for c in self.children],subject_dependencies)
#             if len(self.explSubj)!=1:
#                 return []
            
            
    
    def is_conjunction_predicate(self):
        self.conjResult = []
        conjChildIndList = any_in([c.parent_relation for c in self.children], conjunction_dependencies)
        if not conjChildIndList:
            return False
        childrenCopy = [x for x in self.children]
        self.children = [x for i,x in enumerate(self.children) if i not in conjChildIndList and 
                         x.parent_relation !='conj']
        self.baseElm = copy.copy(self)
        self.children = childrenCopy
        
        cc = []
        conjElements = []
        for child in self.children:
            if child.parent_relation == 'cc':
                if cc and (cc[-1][0] != child.id-1):
                    self.conjResult.append((copy.copy(cc),copy.copy(conjElements)))
                    cc = []
                    conjElements = []
                cc.append((child.id,child.word))
                
                    
            elif child.parent_relation == 'conj':
                conjElements.append(child)              
        
        if cc:
            self.conjResult.append((copy.copy(cc),copy.copy(conjElements)))
        
        return True
        
    def _PREPOSITIONAL_PREDICATE_FEATURE_psubj(self):
        childrenCopy = [x for x in self.children]
        self.children = [x for i,x in enumerate(self.children) if i not in self.prepChildIndList]
        #self.children.remove(self.children[self.possChild[0]])
        d = {}#self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),#self.get_original_sentence(False),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret
    
    def _PREPOSITIONAL_PREDICATE_FEATURE_pobj(self):
        prepChild = self.children[self.prepChildInd]
        if not prepChild.children:
            return {"Value":False,
                    "Span":{}}
        pobjChildren = any_in([c.parent_relation for c in prepChild.children], ["pobj"])
        pcompChildren = any_in([c.parent_relation for c in prepChild.children], ["pcomp"])
        if (len(pobjChildren)>1) or (len(pcompChildren)>1):
            print pobjChildren
            print self.word
            print GraphParsingException("misproper handling for more than one pobj child " +self.report())
        
        if pobjChildren:
            pobjChild = prepChild.children[pobjChildren[0]]
        else:
            pobjChild = False
        if pcompChildren:
            pcompChild = prepChild.children[pcompChildren[0]]
        else:
            pcompChild = False
        
        
        retChild = pcompChild
        #stick obj child under compchild
        if pcompChild and pobjChild:
            pcompChild.children.append(pobjChild)
            pobjChild.parent = pcompChild
            pobjChild.parent_id = pcompChild.id
        elif pobjChild:
            retChild = pobjChild
            
        if not retChild:
            #TODO: no pcomp and no pobj - return the prep child itself
            retChild = prepChild
        
        else:
        
            notPobjChildren = [x for i,x in enumerate(prepChild.children) if i not in pobjChildren+pcompChildren]
            # workaround to deal with cases where there're more than just pobj children - put them all under pobj
            for curChild in notPobjChildren:
                retChild.children.append(curChild)
                curChild.parent = retChild
                curChild.parent_id = retChild.id
        
        if (retChild.word.lower() == "to") and len(retChild.children)==1:
            retChild = retChild.children[0]
            self.prepType += " to"
            
        
        #self.children.remove(self.children[self.possChild[0]])
        #d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":retChild,
               "Span":{}}
        return ret



    # get the possessor of a possessive construction
    def _POSSESSIVE_PREDICATE_FEATURE_Possessor(self):
        poss = self.children[self.possChild[0]]
        childrenCopy = [x for x in poss.children]
        poss.children = [x for x in poss.children if x.parent_relation != POSSESSIVE_LABEL]
        d = poss._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(poss),#poss.get_original_sentence(False),
               "Span":d.keys()}
        poss.children = childrenCopy
        return ret
    
    # get the possessive instrument of a possessive construction
    def _POSSESSIVE_PREDICATE_FEATURE_Possessive(self):
        poss = self.children[self.possChild[0]]
        possesive_children = [x for x in poss.children if x.parent_relation == POSSESSIVE_LABEL]
        if len(possesive_children)>1:
            raise GraphParsingException("more than one possessive child")
        
        if not(possesive_children): #e.g. "their woman"
            return {"Value":False,
                    "Span":False}
            
        possessive_child = possesive_children[0]
        d = possessive_child._get_subtree_nodes(includeHead = True)
        ret = {"Value":possessive_child,#poss.get_original_sentence(False),
               "Span":d.keys()}
        return ret
    
    # get the Possessed of a possesive construction
    def _POSSESSIVE_PREDICATE_FEATURE_Possessed(self):
        childrenCopy = [x for x in self.children]
        if (self.possChild[0] >= len(self.children)):
            print "stub" 
        self.children = [x for i,x in enumerate(self.children) if i!=self.possChild[0]]
        #self.children.remove(self.children[self.possChild[0]])
        d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),#self.get_original_sentence(False),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret

    # get the left side of apposition
    def _APPOSITIONAL_PREDICATE_FEATURE_Left_Side(self):
        # if this is a weird sentence - more than two appositional children - ignore it
        
        """ this was removed for graph appos construction
        """
        #if (len(self.apposChild) > 1):
        #    return False,False
        
        
        childrenCopy = [x for x in self.children]
        self.children = [x for x in self.children if x not in self.apposChild]
        d = self._get_subtree_nodes(includeHead = True)
        ret = {"Value":copy.copy(self),#self.get_original_sentence(False),
               "Span":d.keys()}
        self.children = childrenCopy
        return ret
    
    # get the right side of apposition
    def _APPOSITIONAL_PREDICATE_FEATURE_Right_Side(self):
        """ this was removed for graph appos construction
        """
#         if (len(self.apposChild) > 1):
#             return False,False
        
        
        #childrenCopy = [x for x in self.children]
        #self.children = self.apposChild
        d = self.apposChild[0]._get_subtree_nodes(includeHead = False)
        ret = {"Value":self.apposChild[0],#self.apposChild[0].get_original_sentence(False),
               "Span":d.keys()}
        #self.children = childrenCopy
        return ret
        
    
    def _VERBAL_PREDICATE_SUBTREE_Adv(self):
        pat = Tree("self.parent_relation=='advmod'",
               [Tree("(self.parent_relation=='advmod') and (len(self.children)==0)",[]),
                Tree("$+(self.parent_relation=='ccomp')",
                     [Tree("(self.parent_relation=='mark') and (len(self.children)==0)",[])])])
        # pat identifies instances such as "as much as"
        children_copy = self.children
        adverb_children,non_adverb_children = double_filter(adverb_child_func,self.children)
        self.adverb_children = []
        for curChild in adverb_children:
            ls = find_tree_matches(tree=curChild,pat=pat)
            if ls:
                top = ls[0][0]
                advmod = ls[0][1][0]
                ccomp = ls[0][2][0]
                mark = ls[0][2][1][0]
                self.adverb_children.append((ccomp,
                                             [(t.id,t.word) for t in [advmod,top,mark]]))
                ccomp.children.remove(mark)
                top.children.remove(advmod)
                
            elif curChild.parent_relation != 'advcl':
                self.adverb_children.append((curChild,False))
            else:
                non_adverb_children.append(curChild)
        
            
        self.children = non_adverb_children
        self.adverb_subj = copy.copy(self)
        self.children = children_copy
        return self.adverb_children
    
    # if this predicate is a clausal complement of its ancestor and it has a TO child, it is defined as an infinitive
    def _DONT_RUN_VERBAL_PREDICATE_FEATURE_TODO_Infinitive(self):
        ret = [False,[]]
        if self.parent_relation in clausal_complement:
            to_children = filter(lambda x:x.pos == TO, self.children)
            ret[1].extend([c.id for c in to_children])
        if ret[1]:
            ret[0] = True
        return ret




    def _EXPERIMENTAL_VERBAL_PREDICATE_FEATURE_Infinitive(self):
        xcomp_children = filter(lambda x:x.get_parent_relation() in clausal_complement, self.children)
        ret = ([],[])
        for xcomp_child in xcomp_children:
            aux_children = filter(lambda x:x.get_parent_relation() in aux_dependencies, xcomp_child.children)
            to_children = filter(lambda x:x.pos == TO, aux_children)
            if not to_children:
                return (False,False)
            assert (len(to_children)==1)
            to_child = to_children[0]
            subj_children = filter(lambda x:x.get_parent_relation() in subject_dependencies, xcomp_child.children)
            adv_children = filter(lambda x:x.get_parent_relation() in adverb_dependencies, self.children)
#           if subj_children:
#               print(" ".join([self.word,subj_children[0].word,to_child.word,xcomp_child.word]))
#           if adv_children:
#               print(" ".join([adv_children[0].word,self.word,to_child.word,xcomp_child.word]))
            #ids = [x.id for x in [xcomp_child,to_child]]
            words = " ".join([self.word,to_child.word,xcomp_child.word])
            ret[1].extend([self.id,to_child.id,xcomp_child.id])
            # chaining
            childRes = xcomp_child._VERBAL_PREDICATE_FEATURE_Infinitive()
            if childRes[0]:
                words += " "+" ".join(childRes[0][0].split(" ")[1:])


            ret[0].append(words)

        return ret
    
    


    # return the node that is the head of the phrase between the indexes and a list of the children outside the phrase.
    # in case there is no one head, returns None
    def get_head_of_phrase(self,begin_index, end_index):

        if self.is_id_in_subtree(begin_index) == False or self.is_id_in_subtree(end_index) == False:
                return None

        nodes_list =  [node for node in self.collect_nodes_list_by_ids(begin_index,end_index)]
        nodes_list.sort()
        out_parent = None
        head = self
        out_children = []

        for node in nodes_list:
            if node.get_parent() not in nodes_list: # node's parent is not inside the phrase
                if out_parent: # outside parent was already assigned --> no head for this phrase
                    return None
                else:
                    out_parent = node.get_parent()
                    head = node
                # add the children that are outside the phrase to out_children
                children = node.get_children()
                for child in children:
                    if child not in nodes_list:
                        if child not in out_children:
                            out_children.append(child)

        return head,out_children


    # return True if the id is exists in this tree
    def is_id_in_subtree(self,id):
          if self.id == id:
                return True
          for child in self.children:
                if child.is_id_in_subtree(id):
                     return True
          return False


    # returns  list of range of nodes
    def collect_nodes_list_by_ids(self,id1,id2):
        if self.id >= id1 and self.id <= id2:
            yield self
        for child in self.children:
            for node in child.collect_nodes_list_by_ids(id1,id2):
                yield node

    # return list of nodes that satisfy predicate
    def search(self, predicate):
        if predicate(self):
            yield self
        for c in self.children:
            for res in c.search(predicate):
                yield res

    def get_tree_span(self):
        nodes = self.search(lambda x: x)
        ids = [x.id for x in nodes]
        _min = min(ids)
        _max = max(ids)
        return _min,_max

    # add the function-tags in const_tree to the list function_tags of the relevant nodes in dependency tree
    def mark_function_tags(self, const_tree):
         for f_tag in function_tags:
              search_result = const_tree.search(lambda x: x.name.find("-"+f_tag) > -1 )
              for const_node in search_result:
                    begin_index,end_index = const_node.get_leaves_indexes()
                    phrase_head_result = self.get_head_of_phrase(begin_index,end_index)
                    if phrase_head_result != None:
                         head, out_ch = phrase_head_result
                         head.function_tag.append(f_tag)
                         head.constituent = const_node.name.split("-")[0]

    def mark_nominals(self, nombank_ann,const_t):
        for ann in nombank_ann:
            con_nodes = list(const_t.search(lambda x: x.is_leaf() and ann.token_id + 1 == x.id))
            dep_nodes = list(self.search(lambda x: x.id == con_nodes[0].dep_id))
            dep_nodes[0].is_nominal = True
            for arg in ann.arguments:
                name, tag, tokens_list = arg
                if len(tokens_list) == 1:
                    token,hop = tokens_list[0]
                    const_node = (list(const_t.search(lambda x: x.is_leaf() and token + 1 == x.id)))[0]
                    if hop > 0:
                        for i in range(0,hop):
                            const_node = const_node.parent
                    if const_node == None:
                        continue
                    begin_index,end_index = const_node.get_leaves_indexes()
                    phrase_head_result = self.get_head_of_phrase(begin_index,end_index)
                    if phrase_head_result != None:
                        head, out_ch = phrase_head_result
                        if out_ch == []:
                            head.nominal_argument = (name,tag,dep_nodes[0].id)
                        else:
                            if const_node.as_words() != dep_nodes[0].word:
                                None # argument is the same as the relation
                            else:
                                None # TODO : investigate outside children
                    else:
                        None # TODO : investigate unconsistent subtrees in phrase and dependency trees
                else:
                   None # TODO : handle non-subtree arguments


    def get_head_of_time_phrase(self,begin_index, end_index):

           get_head_of_phrase_result = self.get_head_of_phrase(begin_index, end_index)

           if get_head_of_phrase_result == None:
                 return None

           head,out_children = get_head_of_phrase_result

           if out_children == []:
                 return head

           for child in out_children:
                    if child.get_parent_relation() == "possessive":
                          continue
                    if child.get_parent_relation() == "det":
                          continue
                    if child.get_parent_relation() == "punct":
                          continue
                    if child.get_parent_relation() == "quantmod":
                          continue
                    if child.children == [] and child.get_parent_relation() in mod_labels:
                          continue
                    else:
                          return None

           return head



def double_filter(f,ls):
    sucess=[]
    fail = []
    for x in ls:
        if f(x):
            sucess.append(x)
        else:
            fail.append(x)
    return (sucess,fail)

def find_tree_matches(tree,pat):
    """
    Get all subtrees matching pattern
    
    @type  tree: DepTree
    @param tree: tree in which to search for matches

    @type  pat: nltk.Tree
    @param pat: a pattern to match against tree
    
    @rtype:  list [unification of pat]
    @return: all possible unification of pat in tree
    """


    ret = []
    curMatch = tree.match(pat)
    if curMatch:
        ret.append(curMatch)
    for c in tree.children:
        ret.extend(find_tree_matches(c,pat))
    return ret


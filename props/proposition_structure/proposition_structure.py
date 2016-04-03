from __future__ import division
from proposition import Proposition
from constituency_tree.definitions import *
from dependency_tree.definitions import *
from dependency_tree.tree import DepTree
import dependency_tree
import syntactic_item

PROPS = "Propositions"
ORIG_SENTENCE = "Original Sentence"
COMMENTS = "comments"
NODES = "nodes"
LINKS = "links"

global nodeCounter
nodeCounter = -1


def create_node(text,features,isPredicate=False):
    global nodeCounter
    nodeCounter += 1
    
    color = "#080808" # black
    if isPredicate: color = "#D11919" #red
    
    return {"id": nodeCounter,
            "text":text,
            "features":features,
            "color": color}

def create_link(source,target):
    return {"source": source, "target": target, "right": True, "left": False}

def access_prop(p,keys):
    ret = []
    for k in keys:
        if k in p.pred.feats:
            if p.pred.feats[k]:
                val = p.pred.feats[k]["Value"]
                if isinstance(val,dependency_tree.tree.DepTree):
                    valStr = val.get_original_sentence(False)
                else:
                    valStr = val
                ret.append((k,valStr))
    return ret

def print_prop(p,name,keys):
    ret = name+"{\n"
    for k,val in access_prop(p,keys):
        ret += "{0}\t{1}\n".format(k,val)
    ret += "}\n"
    return ret

printVerbal   = lambda p:print_prop(p,"Verbal",["Head","Negation","Passive Voice","Time","Lemma"])
printPoss   = lambda p:print_prop(p,"Possessive",["Possessor","Possessed"])
printAppos  = lambda p:print_prop(p,"Apposition",["Left Side","Right Side"])
printAdj    = lambda p:print_prop(p,"Adjectival",["Adjective","Subject"])
printCop    = lambda p:print_prop(p,"Copular",["Copular Predicate","Copular Object"])
printCond   = lambda p:print_prop(p,"Conditional",["Condition","Outcome"])
printRCmod  = lambda p:print_prop(p,"RCMOD",["Prop"])


def graphCopular(p):
    copFeats = ["Copular Predicate","Copular Object"]
    vals = dict(access_prop(p, copFeats))
    nodes = [create_node(curNodeText, "",isPredicate = curIsPred) for curNodeText,curIsPred in 
             [("BE",True)] + [(vals[curFeat],False) for curFeat in copFeats]]
    links = [create_link(curSource, curTarget) for curSource,curTarget in [(0,1),(0,2)]]
    return nodes,links
    



#                                                       DepTree.is_copular_predicate,
# coinditional 
# relative
# a class to represent a sentence in a proposition structure, holds a list of interlinked propositions
class PropositionStructure:

    # receives a dep tree representing a sentence, extracts all predicates and initiates Propositions
    def __init__(self,depTree,sentenceId,const_t=0,time_annotations=0,nombank=0):
        if const_t:
            depTree.mark_function_tags(const_t)
        if nombank:
            depTree.mark_nominals(nombank,const_t)
            
        

        self.sentenceId = sentenceId
        self.constTree = const_t
        self.depTree = depTree
        self.originalSentence = self.depTree.get_original_sentence()
        self.numOfWords = len(self.originalSentence.split())
        

        self.propositions= {}
        #self.predicates = depTree.collect_predicates([DepTree.is_copular_predicate])
        self.predicates = depTree.collect_predicates([DepTree.is_verbal_predicate,
                                                      DepTree.is_appositional_predicate,
                                                      DepTree.is_adjectival_predicate,
                                                      DepTree.is_copular_predicate,
                                                      DepTree.is_possesive_predicate,
                                                      DepTree.is_conditional_predicate,
                                                      DepTree.is_relative_clause,
                                                      DepTree.is_nominal_predicate])
        
        
        self.printFunctions= {syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX:printVerbal,
                              syntactic_item.APPOSITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX:printAppos,
                              syntactic_item.ADJECTIVAL_PREDICATE_FEATURE_FUNCTION_PREFIX:printAdj,
                              syntactic_item.COPULAR_PREDICATE_FEATURE_FUNCTION_PREFIX:printCop,
                              syntactic_item.POSSESSIVE_PREDICATE_FEATURE_FUNCTION_PREFIX:printPoss,
                              syntactic_item.CONDITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX:printCond,
                              syntactic_item.RELCLAUSE_PREDICATE_FEATURE_FUNCTION_PREFIX:printRCmod}
        
        
        
        self.graphFunctions= {syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX:False,
                              syntactic_item.APPOSITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX:False,
                              syntactic_item.ADJECTIVAL_PREDICATE_FEATURE_FUNCTION_PREFIX:False,
                              syntactic_item.COPULAR_PREDICATE_FEATURE_FUNCTION_PREFIX:graphCopular,
                              syntactic_item.POSSESSIVE_PREDICATE_FEATURE_FUNCTION_PREFIX:False,
                              syntactic_item.CONDITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX:False,
                              syntactic_item.RELCLAUSE_PREDICATE_FEATURE_FUNCTION_PREFIX:False}
        
        self.propCount = 0
        for l in self.predicates:
            if l:
                self.propCount += 1
        #self.propCount = reduce(lambda x,y:x+len(y), self.predicates,0)
        self.propPerWord = self.propCount / self.numOfWords
        
        
        
        self.pref=    [syntactic_item.APPOSITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            syntactic_item.ADJECTIVAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            syntactic_item.COPULAR_PREDICATE_FEATURE_FUNCTION_PREFIX,
            syntactic_item.POSSESSIVE_PREDICATE_FEATURE_FUNCTION_PREFIX,
            syntactic_item.CONDITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            syntactic_item.RELCLAUSE_PREDICATE_FEATURE_FUNCTION_PREFIX]
        
        # verbal
        self.propositions[syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX] = []
        for verbSubtree in self.predicates[0]:
            time_ann_of_verb,tmp_function_tag_of_verb = self.collect_time_indications(verbSubtree,const_t,time_annotations)
            self.propositions[syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX].append(Proposition(predSubtree=verbSubtree,
                                                 predicate_prefix = syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
                                                 argument_prefix = syntactic_item.VERBAL_ARGUMENT_FEATURE_FUNCTION_PREFIX,
                                                 time_ann_of_verb = time_ann_of_verb,
                                                 tmp_function_tag_of_verb = tmp_function_tag_of_verb))
        # all the others
        for subtrees,prefix in zip(self.predicates[1:],self.pref):
            self.propositions[prefix] = []
            for subtree in subtrees:
                self.propositions[prefix].append(Proposition(subtree,prefix))
                
    def printPS(self):
        ret = '{0}\t{1}\t{2}\t{3}\t"{4}"\n'.format(self.sentenceId,self.propCount,self.numOfWords,self.propPerWord,self.originalSentence)
        ret+= "{\n"
        for prefix in [syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX]+self.pref:
            for p in self.propositions[prefix]:
                if self.printFunctions[prefix]:
                    ret += self.printFunctions[prefix](p)
        ret+= "}\n"
        return ret
    
    def toGraph(self):
        comments = self.printPS()
        
        nodes = []
        links = []
        
        for prefix in [syntactic_item.VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX]+self.pref:
            for p in self.propositions[prefix]:
                if self.graphFunctions[prefix]:
                    curAdd = self.graphFunctions[prefix](p)
                    nodes += curAdd[0]
                    links += curAdd[1]
        
        
#         nodes = [{"id": 1,
#                   "text":"a",
#                   "features":"",
#                   "color": "#080808"}]
#         
#         links = []
        
        ret = {NODES:nodes,
               LINKS:links,
               COMMENTS:comments}
        
        return ret
             
   
    def collect_time_indications(self,verbSubtree,const_t,time_annotations):
        time_ann_of_verb = 0
        tmp_function_tag_of_verb = 0

        if time_annotations:
            time_ann_of_verb = []
            for ta in time_annotations:
                head = verbSubtree.get_head_of_time_phrase(ta.begin_token_index, ta.end_token_index)
                if head and verbSubtree == head.get_parent():
                    time_ann_of_verb.append(ta)
        if const_t:
            tmp_function_tag_of_verb = []
            for child in verbSubtree.get_children():
                if TMP in child.function_tag and child.constituent != PP and child.constituent[0]!=S :
                    tmp_function_tag_of_verb.append(child)

        return time_ann_of_verb,tmp_function_tag_of_verb


    def draw(self):
        self.depTree.draw()
        
    def toJson(self):
        return  {PROPS:[x.toJson() for x in self.propositions],
                 ORIG_SENTENCE:self.depTree.get_original_sentence()}
        #"Uncovered Spans":self.calculate_uncovered_spans()}
        
#     def __getitem__(self,key):
#         return {PROPS:[x.toJson() for x in self.propositions],
#                  ORIG_SENTENCE:self.originalSentence.get_original_sentence()}[key]
                 
    #calculate spans for which no argument or predicate took under its span
    def calculate_uncovered_spans(self):
        
        subTreeDic = self.depTree._get_subtree_nodes(includeHead = False)
        sortedWords = [subTreeDic[k].word for k in sorted(subTreeDic)]
        # init return value to none covered
        coveredMap = dict([(k,False) for k in subTreeDic.keys()])
        
        for prop in self.propositions:
            # get covered spans from predicate
            coveredSpans = [feat["Span"] for feat in prop.pred.feats.values() if feat["Span"]]
            # get covered spans from args
            for arg in prop.arguments:
                coveredSpans.extend(feat["Span"] for feat in arg.feats.values() if feat["Span"])
            
            # iterate over covered spans and update return value
            for span in coveredSpans:
                # tuple span is considered as a range
                if isinstance(span, tuple):
                    for x in range(span[0],span[1]+1):
                        coveredMap[x] = True
                # list span is considered as a list of discrete token indices.
                elif isinstance(span,list):
                    for x in span:
                        coveredMap[x] = True
            
        # mark all unneeded pos as covered
        for x in coveredMap:
            if subTreeDic[x].pos in ignore_pos:
                coveredMap[x]=True
        
        #group and return
        ret = []
        startIndex=-1
        coveredMap[max(coveredMap.keys())+1] = True # add a dummy value to close a possible last span
        
        
        
        for x in sorted(coveredMap.keys()):
            x = coveredMap[x]
            if ((not x) and (startIndex==-1)):
                startIndex = x-1
            elif (x and (startIndex != -1)):
                curSpan = (startIndex,x-1)
                rels = [(c.get_parent_relation(),c.get_original_sentence(root=False)) for c in self.depTree.get_children() if c.id in range(curSpan[0]+1,curSpan[1]+1)]
                ret.append((curSpan,
                            " ".join(sortedWords[curSpan[0]:curSpan[1]]),
                            rels))
                startIndex = -1
            
        return ret
        
    
    
    
            

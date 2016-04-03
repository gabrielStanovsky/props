import inspect
from dependency_tree.tree import DepTree
import sys
import datetime

# class to represent a predicate, calculate and store its features

# a prefix by with to identify feature extracting function in the DepTree class
VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX = "_VERBAL_PREDICATE_FEATURE_"
APPOSITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX = "_APPOSITIONAL_PREDICATE_FEATURE_"
ADJECTIVAL_PREDICATE_FEATURE_FUNCTION_PREFIX = "_ADJECTIVAL_PREDICATE_FEATURE_"
COPULAR_PREDICATE_FEATURE_FUNCTION_PREFIX = "_COPULAR_PREDICATE_FEATURE_"
POSSESSIVE_PREDICATE_FEATURE_FUNCTION_PREFIX = "_POSSESSIVE_PREDICATE_FEATURE_"
CONDITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX = "_CONDITIONAL_PREDICATE_FEATURE_"
RELCLAUSE_PREDICATE_FEATURE_FUNCTION_PREFIX = "_RELCLAUSE_PREDICATE_FEATURE_"
VERBAL_ARGUMENT_FEATURE_FUNCTION_PREFIX = "_VERBAL_ARGUMENT_FEATURE_"


PREFIXES = [VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX, 
            APPOSITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            ADJECTIVAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            COPULAR_PREDICATE_FEATURE_FUNCTION_PREFIX,
            POSSESSIVE_PREDICATE_FEATURE_FUNCTION_PREFIX,
            CONDITIONAL_PREDICATE_FEATURE_FUNCTION_PREFIX,
            RELCLAUSE_PREDICATE_FEATURE_FUNCTION_PREFIX,
            VERBAL_ARGUMENT_FEATURE_FUNCTION_PREFIX]



def get_verbal_features(t):
    prefix=VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX
    #get all features names and functions from DepTree class which start with the indicator prefix
    verbalFuncList = SyntacticItem.funcList[prefix]
    feats={}
    
    #iterate over functions and apply on the input
    for (featType,f) in verbalFuncList:
        res = f(t) 
        if res: 
            if isinstance(res, list) or isinstance(res, tuple):
                if res[0]:
                    feats[featType] = res
            else:
                feats[featType] = res
        
    return feats

class SyntacticItem:
    #the list of functions to apply on the input tree, each of these need to
    # conform to:
    #    - input: a dep tree, for which the head represents the predicate
    #    - output: (the name of the feature (string),the value of the feature, its span)
    funcList = dict([(prefix,[(" ".join(fname.split("_")[4:]),f) for fname,f in inspect.getmembers(object=DepTree, predicate=inspect.ismethod)
                if fname.startswith(prefix)]) for prefix in PREFIXES])
    
    #init with a dep tree and calculate the features, in addition receives the prefix by which to choose functions from the dep tree class 
    def __init__(self,predSubtree,prefix,time_ann_of_verb=0,tmp_function_tag_of_verb=0):
        self.prefix=prefix
        self.predSubtree = predSubtree
        #get all features names and functions from DepTree class which start with the indicator prefix
        self.funcList = SyntacticItem.funcList[self.prefix]
        minIndex,maxIndex = -1,-1
        subTreeDic = predSubtree._get_subtree()
        # self.feats holds all the features representing this predicate
        self.feats={}
        self.time_ann_of_verb = time_ann_of_verb
        self.tmp_function_tag_of_verb = tmp_function_tag_of_verb
        
        textValue = {}
        
        #iterate over functions and apply on the input
        for (featType,f) in self.funcList:
            res = f(predSubtree)
            
            # Features can return either (value,span) or a dictionary containing at least these keys
            if isinstance(res,dict):
                self.feats[featType] = res
                span,value = self.feats[featType]['Span'], self.feats[featType]['Value']
            else:
                value,span = f(predSubtree)
                self.feats[featType] = {"Value":value,"Span":span}
            
            # update spans
            if value:
                if isinstance(span,str):
                    span_split = span.split()
                    for i in range(0,len(span_split)):
                        textValue[i] = span_split[i]
                if isinstance(span,tuple):
                    for x in range(span[0],span[1]+1):
                        textValue[x] = subTreeDic[x]
                    if minIndex == -1:
                        minIndex,maxIndex  = span
                    else:
                        minIndex,maxIndex  = min(minIndex,span[0]),max(maxIndex,span[1])
                elif isinstance(span, list):
                    for x in span:
                        textValue[x] = subTreeDic[x]
                        minIndex,maxIndex  = min(minIndex,x),max(maxIndex,x)
                    
           
            
        # text feature is a generic one, that concatenates all the tokens in the shared span of features
        self.feats["Text"] = {"Value":" ".join([textValue[x] for x in sorted(textValue)]),
                              "Span":False}#(minIndex,maxIndex)}
        #self.feats["Text"] = {"Value":" ".join([subTreeDic[x] for x in range(minIndex,maxIndex+1)]),
        #                      "Span":(minIndex,maxIndex)}

#         if self.prefix == VERBAL_PREDICATE_FEATURE_FUNCTION_PREFIX:
#             self.set_time_feat()
#            self.set_tense_feat()


    def set_tense_feat(self):
        if self.feats["Tense"]["Span"]:
            return
        value = ""
        if self.time_ann_of_verb:
            for ta in self.time_ann_of_verb:
                if ta.ref:
                    value = ta.ref.lower()
                elif ta.parsed_value:
                    now = datetime.datetime.now()
                    if ta.parsed_value > now:
                        value = "future"
                    elif ta.parsed_value < now:
                        value = "past"
                    else:
                        value = "present"
                else:
                    continue
                self.feats["Tense"] = {"Value":value,
                          "Span":range(ta.begin_token_index, ta.end_token_index+1)}
                break




    def set_time_feat(self):
        values_list = []
        span = []
        # function tag TMP(constituency tree)
        if self.tmp_function_tag_of_verb:
            for node in self.tmp_function_tag_of_verb:
                node_min_span, node_max_span = node.get_tree_span()
                span += range(node_min_span,node_max_span+1)
                values_list.append(node.get_original_sentence(False))
            span.sort()
        # tmod (dependency tree)
        elif self.feats["Time"]["Span"]:
            span = self.feats["Time"]["Span"]
            values_list = self.feats["Time"]["Value"]
            span.sort()
        # stanford time-annotator
        elif self.time_ann_of_verb:
            for ta in self.time_ann_of_verb:
                span = range(ta.begin_token_index, ta.end_token_index+1)
                values_list.append(ta.time_expression)
        else:
            return
        self.feats["Time"] = {"Value":"/".join(values_list),
                              "Span":span}


    def toJson(self):
        return self.feats
##
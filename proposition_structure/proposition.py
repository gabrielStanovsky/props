from syntactic_item import *
from dependency_tree.definitions import *

# class to represent a single proposition, holds a predicate and its arguments
class Proposition:
    #init receives a subtree and initiates its predicate and arguments
    def __init__(self,predSubtree,predicate_prefix,argument_prefix="",time_ann_of_verb=0,tmp_function_tag_of_verb=0):
        self.predSubtree = predSubtree
        self.pred = SyntacticItem(predSubtree,predicate_prefix,time_ann_of_verb,tmp_function_tag_of_verb)
        if argument_prefix:
            self.arguments = [SyntacticItem(argumentTree,argument_prefix) 
                              for argumentTree in self.predSubtree.collect_arguments()]
        else:
            self.arguments = []
    
    #calculate spans for which no argument or predicate took under its span
    def calculate_uncovered_spans(self):
        
        subTreeDic = self.predSubtree._get_subtree_nodes(includeHead = True)
        sortedWords = [subTreeDic[k].word for k in sorted(subTreeDic)]
        # init return value to none covered
        coveredMap = dict([(k,False) for k in subTreeDic.keys()])
        
        # get covered spans from predicate
        coveredSpans = [feat["Span"] for feat in self.pred.feats.values() if feat["Span"]]
        # get covered spans from args
        for arg in self.arguments:
            coveredSpans.extend(feat["Span"] for feat in arg.feats.values() if feat["Span"])
        
        # iterate over covered spans and update return value
        for span in coveredSpans:
            # tuple span is considered as a range
            if isinstance(span, tuple):
                for i in range(span[0],span[1]+1):
                    coveredMap[i] = True
            # list span is considered as a list of discrete token indices.
            elif isinstance(span,list):
                for i in span:
                    coveredMap[i] = True
        
        # mark all unneeded pos as covered
        for i in coveredMap:
            if subTreeDic[i].pos in ignore_pos:
                coveredMap[i]=True
        
        #group and return
        ret = []
        startIndex=-1
        coveredMap[max(coveredMap.keys())+1] = True # add a dummy value to close a possible last span
        
        
        
        for i in sorted(coveredMap.keys()):
            x = coveredMap[i]
            if ((not x) and (startIndex==-1)):
                startIndex = i-1
            elif (x and (startIndex != -1)):
                curSpan = (startIndex,i-1)
                rels = [(c.word,c.get_parent_relation(),c.get_original_sentence(root=False),c) 
                        for c in self.predSubtree.get_children() 
                        if c.id in range(curSpan[0]+1,curSpan[1]+1)]
                ret.append((curSpan,
                            " ".join(sortedWords[curSpan[0]:curSpan[1]]),
                            rels))
                startIndex = -1
        
        return ret

        
    def __toDic__(self):
        d = self.predSubtree._get_subtree()
        return {"Predicate":self.pred.toJson(),
                "Arguments":[x.toJson() for x in self.arguments],
                "Uncovered Spans":self.calculate_uncovered_spans(),
                "Text":" ".join(d[k] for k in sorted(d))}
    
    def toJson(self):
        return self.__toDic__()
    
    def __getitem__(self,key):
        return self.__toDic__()[key]
    
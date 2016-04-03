import graph_representation.node
from graph_representation.graph_wrapper import GraphWrapper
from graph_representation.word import Word, NO_INDEX
from graph_representation.node import Node,CopularNode,PossessiveNode,PropNode,\
    AppositionNode, PrepNode, CondNode, ConjunctionNode, advNode, RCMODPropNode,\
    TimeNode, isTime, LocationNode, isLocation
from dependency_tree.definitions import adjectival_mod_dependencies, labels_ban,\
    filter_labels_ban, condition_outcome_markers, reason_outcome_markers,\
    comp_markers

import graph_utils
from proposition_structure import syntactic_item
from graph_representation import word
from time_annotator.timex_wrapper import timexWrapper
from mx.DateTime.ISO import ParseTime
from location_annotator.textual_location_annotator import textualLocationAnnotator

FIRST_ENTITY_LABEL = "entity"#"first_entity"
SECOND_ENTITY_LABEL = "entity"#"second_entity"
POSSESSOR_LABEL = "possessor"
POSSESSED_LABEL = "possessed"
COMP_LABEL = "comp"
DISCOURSE_LABEL = "discourse"
OUTCOME_LABEL = "outcome"
CONDITION_LABEL = "condition"
REASON_LABEL = "reason"
ADV_LABEL = "adverb"
SORUCE_LABEL = "source"

#types for appendix:
APPENDIX_PREP  = "Prepositions"
APPENDIX_COP   = "Copular"
APPENDIX_POSS  = "Possessives"
APPENDIX_APPOS = "Appositions"
APPENDIX_ADJ   = "Adjectives"
APPENDIX_VERB  = "Verbal Predicates"
APPENDIX_COND  = "Conditionals and Temporals"
APPENDIX_COMPLEMENT = "Clausal Complements"
APPENDIX_RCMOD  = "Relative Clauses"
APPENDIX_CONJUNCTION  = "Conjunctions"
APPENDIX_NEGATION  = "Negation"
APPENDIX_PASSIVE  = "Passive Voice"
APPENDIX_LEMMA  = "Lemma"
APPENDIX_LOCATION  = "Locations"
APPENDIX_MODAL  = "Modal"
APPENDIX_EXISTENSIALS = "Existensials"
APPENDIX_TENSE = "Tense"
APPENDIX_TIME = "Time"
APPENDIX_RANGE = "Ranges"

APPENDIX_KEYS = (APPENDIX_ADJ,
                 APPENDIX_APPOS,
                 APPENDIX_COND,
                 APPENDIX_CONJUNCTION,
                 APPENDIX_COMPLEMENT,
                 APPENDIX_COP,
                 APPENDIX_EXISTENSIALS,
                 APPENDIX_LEMMA,
                 APPENDIX_LOCATION,
                 APPENDIX_MODAL,
                 APPENDIX_NEGATION,
                 APPENDIX_PASSIVE,
                 APPENDIX_POSS,
                 APPENDIX_PREP,
                 APPENDIX_RANGE,
                 APPENDIX_RCMOD,
                 APPENDIX_TENSE,
                 APPENDIX_TIME,
                 APPENDIX_VERB
                 )


class ParseGraph:
    """
    class to bunch together all function of conversion from DepTree to digraph
    Mainly in order to store the graph as a member which all these functions can edit.   
    """
    def __init__(self,t,locationAnnotator):
        """
        initialize a graph class, followed by converting a tree
    
        @type  t: Tree
        @param tree: syntactic tree to be converted
        
        @type  id: int
        @param id: a unique id for current Tree
        
        @type gr: digraph
        @var  gr: the graph representing t
        """
        if not t.id:      # meaning this is the ROOT element
            self.tree = t.children[0]
        else:
            self.tree = t    
        self.gr = GraphWrapper(t.get_original_sentence())
        
        self.locationAnnotator = locationAnnotator
        
        # maintain an appendix for easier browsing
        self.types = appendix_types()
        
        self.parse(self.tree)
        
    def parse(self,t):
        """
        Get the graph representation from a syntactic representation
        Returns through the graph parameter.
        
        @type  t: DepTree
        @param tree: syntactic tree to be converted
        
        @rtype: Node
        @return: the node in the graph corresponding to the top node in t
        """
        
        #order matters!
        if t.is_conditional_predicate():
            self.types.add(APPENDIX_COND)
            return self.parseConditional(outcome = t._CONDITIONAL_PREDICATE_FEATURE_Outcome()["Value"],
                                         condList = t.condPred)

        
        if t._VERBAL_PREDICATE_SUBTREE_Adv():
            advChildren = t.adverb_children
            advSubj = t.adverb_subj
            return self.parseAdverb(subj=advSubj, 
                             advChildren=advChildren)
        
        if t.is_conjunction_predicate():
            self.types.add(APPENDIX_CONJUNCTION)
            return self.parseConjunction(baseElm = t.baseElm,
                                         conjResult = t.conjResult)
        
        if t.is_appositional_predicate():
            self.types.add(APPENDIX_APPOS)
            firstEntity = t._APPOSITIONAL_PREDICATE_FEATURE_Left_Side()["Value"]
            secondEntity = t._APPOSITIONAL_PREDICATE_FEATURE_Right_Side()["Value"]
            return self.parseApposition(index = t.id,
                                        first_entity=firstEntity,
                                        second_entity=secondEntity)
        
        if t.is_relative_clause():
            self.types.add(APPENDIX_RCMOD)
            return self.parseRcmod(np = t._RELCLAUSE_PREDICATE_FEATURE_Rest()['Value'], 
                                   modList = t.rcmodPred)
        
        if t.is_prepositional_predicate():
            self.types.add(APPENDIX_PREP)
            return self.parsePreposition(psubj=t._PREPOSITIONAL_PREDICATE_FEATURE_psubj()["Value"],
                                          prepChildList=t.prepChildList)
                    
        if t.is_copular_predicate():
            self.types.add(APPENDIX_COP)
            firstEntity = t._COPULAR_PREDICATE_FEATURE_Copular_Predicate()["Value"]
            secondEntity = t._COPULAR_PREDICATE_FEATURE_Copular_Object()["Value"]
            return self.parseCopular(index = t.id,
                                     first_entity=firstEntity,
                                     second_entity=secondEntity,
                                     features = syntactic_item.get_verbal_features(t))
        
        if t.is_possesive_predicate():
            self.types.add(APPENDIX_POSS)
            possessor = t._POSSESSIVE_PREDICATE_FEATURE_Possessor()["Value"]
            possessed = t._POSSESSIVE_PREDICATE_FEATURE_Possessed()["Value"]
            possessive = t._POSSESSIVE_PREDICATE_FEATURE_Possessive()["Value"]
            return self.parsePossessive(possessor = possessor, 
                                        possessed = possessed,
                                        possessive = possessive)
        
            
        if t.is_adjectival_predicate():
            self.types.add(APPENDIX_ADJ)
            return self.parseProp(subject = t._ADJECTIVAL_PREDICATE_FEATURE_Subject()["Value"],
                                  copulaIndex = NO_INDEX,
                                  adjectiveChildList = t.adjectivalChildList,
                                  propAsHead=False)
            
        if t.is_clausal_complement():
            self.types.add(APPENDIX_COMPLEMENT)
            return self.parseComplement(compSubj = t.compSubj,
                                        compChildren = t.compChildList)
        
        if t.unhandled_advcl():
            # put each unhandled advcl as a disconnected subgraph
            for c in t.advcl:
                self.parse(c)
            return self.parse(t)
        
        if t.is_verbal_predicate():
            self.types.add(APPENDIX_VERB)
            head_ret = t._VERBAL_PREDICATE_SUBTREE_Head()
            return self.parseVerbal(indexes = head_ret["Span"],
                             verbs = head_ret["Value"].split(" "),
                             arguments = t.collect_arguments(),
                             tree = t)
        
            
        
        else:
            # fall back - pack all the tree in a single node
            if len(t.children)==1:
                if (t.children[0].parent_relation == "nn") and (t.word.endswith(",")) and (t.children[0].word.endswith(",")):
                    #conjunction in disguise
                    child = t.children[0]
                    t.children = []
                    ret =  self.parseConjunction(cc = [(t.id,"and")], 
                                                conjElements = [t,child])
                    t.children = [child]
                    return ret
            
            nodes = t._get_subtree(filter_labels_ban)
            text = [Word(index=index,
                         word=nodes[index]) for index in sorted(nodes.keys())] 
            topNode = self.parseBottom(text = sorted(text,key=lambda x:x.index),
                        features = syntactic_item.get_verbal_features(t))

            return topNode
    

    def parseBottom(self,text,features):
        """
        Parse a node for which all other construction test has failed,
        no tree structure is assumed over the input text.
        
        @type  text: list[Word]
        @param text: words to appear at node, oredered by index
        
        @type  features: dict{string:string}
        @param features: features of the node
        
        @rtype  Node
        @return the node which was inserted into the graph
        """
        time_res = timexWrapper(text)
        if time_res[0]:
            self.types.add(APPENDIX_TIME)
            time_node = self.parseTime(time_res[0])
        else:
            time_node = False
            s = " ".join([w.word for w in text])
            if self.locationAnnotator.is_location(s):
                locNode = LocationNode.init(features={})
                self.gr.add_node(locNode)
                bottomNode = Node(isPredicate=False,
                                  text = text,
                                  features = features,
                                  valid=True)
                self.gr.add_node(bottomNode)
                self.gr.add_edge((locNode,bottomNode),
                                 label="loc")
                self.types.add(APPENDIX_LOCATION)
                return locNode
        
        left_text = time_res[1]
        if left_text:        
            topNode = Node(isPredicate=False,
                           text = left_text,
                           features = features,
                           valid=True)
            if not topNode.str:
                time_node.features.update(topNode.features)
                topNode = time_node
                
            else: 
                self.gr.add_node(topNode)
                if time_node:
                    self.gr.add_edge((topNode,time_node))
            
        else:
            if not time_node:
                #TODO: probably not good, but happens
                topNode = Node(isPredicate=False,
                           text = [],
                           features = features,
                           valid=True)
                self.gr.add_node(topNode)
            else:
                topNode = time_node
        
        return topNode
         
    
    def parseTime(self,time_res):
        """
        Add a time node to the graph, given the results of the automated tool.
        
        @type  time_res: list[TimeExpression]
        @param time_res: Time Expressions to be added to the graph, all as single nodes, and under the same "time" node
         
        @rtype  Node
        @return the top node (time node)
        """
        topNode = TimeNode.init(features={})
        self.gr.add_node(topNode)
        
        for timeExpression in time_res:
            curNode = Node(isPredicate = False,
                           text = timeExpression.text,
                           features = {"Time Value":timeExpression.value},
                           valid = True)
            self.gr.add_node(curNode)
            self.gr.add_edge((topNode,curNode))
        return topNode
    
    def parseComplement(self,compSubj,compChildren):
        """
        add a complement subgraph to the graph
        
        @type  compSubj: DepTree
        @param compSubj: the subject of all following complements
        
        @type  compChildren: list [depTree]  
        @param compChildren: all subclauses
        """         
        
        topNode = self.parse(compSubj)
        
        for child in compChildren:
            curNode = self.parse(child)
            self.gr.add_edge(edge=(topNode,curNode),
                             label=child.parent_relation)
        return topNode
        
    
    def parseConjunction(self,baseElm,conjResult):
        """
        add a conjunction subgraph to the graph
        
        @type  cc: list [(int,string)]
        @param cc: the connecting element
        
        @type  conjElements: list [DepTree]  
        @param conjElements: subtrees to be joined in conjunction
        """
        
        
        retNode = self.parse(baseElm)
        
        for cc,conjElements in conjResult:
        
            if not conjElements:
                # discourse marker
                discourseNode = Node(isPredicate = False,
                                text = [Word(ind,word) for ind,word in cc],
                                features = {},
                                valid=True)
                self.gr.add_node(discourseNode)
            
                self.gr.add_edge(edge =(retNode,discourseNode),
                                 label= DISCOURSE_LABEL)
            else:
                # generate top conjunction node
                conjNode = ConjunctionNode.init(text = [Word(ind,word) for ind,word in cc],
                                      features = {})
                self.gr.add_node(conjNode)
                #connect cc to base element
                self.gr.add_edge((conjNode,retNode))
                
                #generate node for each element and connect to topNode
                for elm in conjElements:
                    curNode = self.parse(elm)
                    self.gr.add_edge(edge = (conjNode,curNode))
            
        return retNode
            
        
    
    def parseRcmod(self,np,modList):
        """
        add a relative clause subgraph to the graph
        
        @type  np: DepTree
        @param np: the entity being modified by the relative clause
        
        @type  modlist: a list of DepTrees,  
        @param modList: trees modifying np
        """
        
        topNode = self.parse(np)
        
        for temp_t in modList:
            # add nodes
            rcmodNode = self.parse(temp_t._RELCLAUSE_PREDICATE_FEATURE_Relclause()["Value"])
            propNode = RCMODPropNode.init(features={},
                                     valid=True)
            self.gr.add_node(propNode)
            
            #add edges
            self.gr.add_edge(edge=(topNode,propNode))
            self.gr.add_edge(edge=(propNode,rcmodNode))
            if rcmodNode.isPredicate:
                # this will create a cycle, label is a hurestic to guess the connection between relative clause and top node
                self.gr.add_edge(edge=(rcmodNode,topNode), label=temp_t.rcmodRel)
            
            # record that this construction came from rcmod
            topNode.rcmod = [propNode,rcmodNode] 
        
        return topNode
        
    
    def parseConditional(self,outcome,condList):
        """
        add a conditional subgraph to the graph
        
        @type  outcome: DepTree
        @param outcome: the outcome of all following conditions
        
        @type  condList: a list of DepTrees,  
        @param condList: all conditionals regarding outcome
        """
        
        outcomeNode = self.parse(outcome)
        
        for temp_t in condList:
            mark = temp_t._CONDITIONAL_PREDICATE_FEATURE_Mark()
            markValue = mark["Value"]
            markIndex = mark["Span"][0]
            conditionNode = self.parse(temp_t._CONDITIONAL_PREDICATE_FEATURE_Condition()["Value"]) 
            
            #create nodes
            markNode = CondNode.init(index = markIndex,
                                condType = markValue,
                                features = {},
                                valid=True)
            self.gr.add_node(markNode)
            
            markValue = markValue.lower()

            # add edges according to the type of conditional
            if markValue in condition_outcome_markers:
                self.gr.add_edge(edge = (markNode,outcomeNode),
                                 label = OUTCOME_LABEL)
                
                self.gr.add_edge(edge = (markNode,conditionNode),
                                 label = CONDITION_LABEL)
            
            elif markValue in reason_outcome_markers:
                self.gr.add_edge(edge = (markNode,outcomeNode),
                                 label = OUTCOME_LABEL)
                
                self.gr.add_edge(edge = (markNode,conditionNode),
                                 label = REASON_LABEL)
            
            elif markValue in comp_markers:
                self.gr.add_edge(edge = (conditionNode,outcomeNode),
                                 label = COMP_LABEL)
            
            else:
                #add edges
                self.gr.add_edge((outcomeNode,markNode))
                self.gr.add_edge((markNode,conditionNode))
    
        #return top node
        return outcomeNode
    
    def parsePreposition(self,psubj,prepChildList):
        """
        add a preposition subgraph to the graph
        
        @type  psubj: DepTree
        @param psubj: the subject of all following prepositions
        
        @type  prepChildList: a list of DepTrees,  
        @param prepChildList: all prepositions regarding nsubj
        """
        
        #create top nodes:
        
        topNode = self.parse(psubj)
        
        for temp_t in prepChildList:
            #generate bottom node and connect to prep
            pobj = temp_t._PREPOSITIONAL_PREDICATE_FEATURE_pobj()["Value"]
            if not pobj: # e.g., #460
                continue
            
            bottomNode = self.parse(pobj)
            
            
            #generate prep node and connect to top node
            prepNode = PrepNode.init(index=temp_t.prepInd,
                                prepType=temp_t.prepType,
                                features={},
                                valid = True)
#             self.gr.add_node(prepNode)
            
            #self.gr.add_edge(edge = (prepNode,bottomNode))
            self.gr.add_edge(edge = (topNode,bottomNode),
                             label = " ".join([w.word for w in prepNode.str]))
            
            
        
            
            
            
            
            
        return topNode
        
    def parseVerbal(self,indexes,verbs,arguments,tree):
        """
        add a verbal subgraph to the graph
        
        @type  indexes: list [int]
        @param indexes: the index(es) of the verb in the sentence
        
        @type  verbs: list [string] 
        @param verbs: the string(s) representing the verb
        
        @type tree: DepTree
        @param tree: tree object from which to extract various features
        
        @type  arguments: list 
        @param arguments: list of DepTrees of arguments
        """
        
        # create verbal head node
        # start by extracting features
        feats = syntactic_item.get_verbal_features(tree)
        if feats['Lemma'] == verbs[0]:
            del(feats['Lemma'])
        
        for k in feats:
            self.types.add(k)
            
            
        verbNode = graph_representation.node.Node(isPredicate=True,
                                                  text = [Word(index=index,
                                                               word=verb) for index,verb in zip(indexes,verbs)],
                                                  features=feats,
                                                  valid=True)
        self.gr.add_node(verbNode)
        
        # handle arguments
        for arg_t in arguments:
            curNode = self.parse(arg_t)
            #curNode.features = syntactic_item.get_verbal_features(arg_t)
            self.gr.add_edge((verbNode,curNode), arg_t.parent_relation)
        
        
        # handle time expressions
        (timeSubtree,_) = tree._VERBAL_PREDICATE_SUBTREE_Time()
        if timeSubtree:
            timeNode = graph_representation.node.TimeNode.init(features = {})
            self.gr.add_node(timeNode)
            timeSubGraph = self.parse(timeSubtree)
            self.gr.add_edge((verbNode,timeNode))
            self.gr.add_edge((timeNode,timeSubGraph))
            
        return verbNode 
        
    def parseAdverb(self,subj,advChildren):
        topNode = self.parse(subj) 
        
        for advChild,mwe in advChildren:
#             advTopNode = advNode.init(features = {})
#             self.gr.add_node(advTopNode)
#             self.gr.add_edge(edge = (topNode,advTopNode))
            if mwe:
                # in case this is a complex adverb ("as long as")
                curAdvNode = Node(isPredicate = False,
                                  text = [Word(ind,word) for ind,word in mwe],
                                  features = {},
                                  valid = True)
                self.gr.add_node(curAdvNode)
                curChildNode = self.parse(advChild)
                self.gr.add_edge(edge=(topNode,curAdvNode),
                                 label = ADV_LABEL)
                self.gr.add_edge(edge = (curAdvNode,curChildNode),
                                 label = advChild.parent_relation)
                
                
                
            else:
                curChildNode = self.parse(advChild)
                self.gr.add_edge(edge = (topNode,curChildNode),
                                 label = ADV_LABEL)

        return topNode 

        
    
    def parseCopular(self,index,first_entity,second_entity,features):
        """
        add a copular subgraph to the graph
        
        @type  index: int
        @param index: the index of the copula in the sentence
        
        @type  first_entity: DepTree
        @param first_entity: the syntax tree of the first entity
        
        @type  second_entity: DepTree
        @param second_entity: the syntax tree of the second entity
        
        @rtype: Node
        @return: the top node of the copula subgraph
        """
        
        if (second_entity.parent_relation in adjectival_mod_dependencies) \
        or (not second_entity.is_definite()):
            # reduce to prop construction when the second element in the copula is an adjective
            # e.g., Rabbit is white -> white rabbit
            # or when the second element is indefinite
            second_entity.adjectivalChild = [second_entity]
            second_entity.relative_adj = False #TODO: calculate this
            second_entity.parent_relation = "copular" #TODO: this might be dangerous :\
            return self.parseProp(subject = first_entity,
                                  copulaIndex = index,
                                  adjectiveChildList = [second_entity],
                                  features=features,
                                  propAsHead = True)
             
        
        # generate the top node and add to the graph
        topNode = CopularNode.init(index=index,
                              features=features, 
                              valid=True)
        self.gr.add_node(topNode)
        
        # generate both entities subgraphs
        firstEntityNode = self.parse(first_entity)
        secondEntityNode = self.parse(second_entity)
        
        #propagate properties between the two nodes
        graph_representation.node.addSymmetricPropogation(firstEntityNode, 
                                                          secondEntityNode)
        
        #add labeled edges
        self.gr.add_edge(edge=(topNode,firstEntityNode),
                         label=FIRST_ENTITY_LABEL)
        self.gr.add_edge(edge=(topNode,secondEntityNode),
                         label=SECOND_ENTITY_LABEL)
        
        return topNode
    

    def parseApposition(self,index,first_entity,second_entity):
        """
        add an apposition subgraph to the graph
        
        @type  index: int
        @param index: the index of the apposition in the sentence
        
        @type  first_entity: DepTree
        @param first_entity: the syntax tree of the first entity
        
        @type  second_entity: DepTree
        @param second_entity: the syntax tree of the second entity
        
        @rtype: Node
        @return: the top node of the apposition subgraph
        """
        
        #copied from copular, interesting to see if this happens
        if (second_entity.parent_relation in adjectival_mod_dependencies) \
        or (not second_entity.is_definite()):
            # reduce to prop construction when the second element in the copula is an adective
            # e.g., Rabbit is white -> white rabbit
            second_entity.adjectivalChild = [second_entity]
            second_entity.relative_adj = False #TODO - calculate this
            second_entity.parent_relation = "appos" #TODO: this might be dangerous :\
            return self.parseProp(subject = first_entity,
                                  copulaIndex = NO_INDEX,
                                  adjectiveChildList = [second_entity],
                                  propAsHead = True)
             
        
        # generate the top node and add to the graph
        topNode = AppositionNode.init(index=index,
                              features={}) 
                              
        self.gr.add_node(topNode)
        
        # generate both entities subgraphs
        firstEntityNode = self.parse(first_entity)
        secondEntityNode = self.parse(second_entity)
        
        # remember first and second entities in apposition's node
#         topNode.entities = [firstEntityNode,secondEntityNode]
        
        # propagate properties between the two nodes
        graph_representation.node.addSymmetricPropogation(firstEntityNode, 
                                                          secondEntityNode)

        #add labeled edges
        self.gr.add_edge(edge=(topNode,firstEntityNode),
                         label=FIRST_ENTITY_LABEL)
        self.gr.add_edge(edge=(topNode,secondEntityNode),
                         label=SECOND_ENTITY_LABEL)
        
        return topNode

    
    
    def parsePossessive(self,possessor,possessed,possessive):
        """
        add a possessive subgraph to the graph
        
        @type  index: int
        @param index: the index of the possessive in the sentence
        
        @type  possessor: DepTree
        @param possessor: the syntax tree of the possessor
        
        @type  possessed: DepTree
        @param possessed: the syntax tree of the possessed
        
        @type  possessive: DepTree
        @param possessive: the syntax tree of the possessive - e.g - 's
        
        @rtype: Node
        @return: the top node of the possessive subgraph
        """
        
        if not possessive:
            index = graph_representation.word.NO_INDEX
        else:
            index = possessive.id
        
        # generate nodes
        possessorNode = self.parse(possessor)
        possessedNode = self.parse(possessed)
        
        if isTime(possessorNode) or isLocation(possessorNode):
            #possessive construction to indicate time
            self.gr.add_edge((possessedNode,possessorNode))
            return possessedNode
        
        #otherwise - proper possessive:
        hasNode = PossessiveNode.init(index=index,
                                 features={}, 
                                 valid=True)
        self.gr.add_node(hasNode)
        
        # add edges to graph
        self.gr.add_edge(edge=(hasNode,possessorNode), 
                         label=POSSESSOR_LABEL)
        self.gr.add_edge(edge=(hasNode,possessedNode), 
                         label=POSSESSED_LABEL)
        
        # create top node
        # get list of all relevant nodes
        nodeLs = [possessorNode,possessedNode]
        
        if possessive: # in some cases there's no possessive marker (e.g., "their woman")
            possessiveNode = graph_representation.node.Node(isPredicate=False,
                                                            text = [Word(possessive.id,
                                                                        possessive.get_original_sentence(root=False))],
                                                            features = {},
                                                            valid=True)
            nodeLs.append(possessiveNode)
        
        
        # create possessive top node, add to graph, and return it
        topNode = graph_utils.generate_possessive_top_node(graph=self.gr, nodeLs=nodeLs)
        self.gr.add_node(topNode)
        
        #mark that features and neighbours should propagate from the top node to the possessed
        # John's results were low -> features should propogate between (John's results) and (results)
        graph_representation.node.addSymmetricPropogation(topNode, possessedNode)
        
        return topNode 
        
    def parseProp(self,subject,copulaIndex,adjectiveChildList,propAsHead,features={}):
        """
        add a prop subgraph to the graph
        
        @type  adjective: DepTree
        @param adjective: the syntax tree of the adjective
        
        @type  subject: DepTree
        @param subject: the syntax tree of the subject
        
        @rtype: Node
        @return: the top node of the copula subgraph
        """
        
        # parse top node
        subjectNode = self.parse(subject)
        topNode = subjectNode
        #parse each property and connect to top node
        for temp_t in adjectiveChildList:
            adjective = temp_t._ADJECTIVAL_PREDICATE_FEATURE_Adjective()["Value"]
            adjectiveNode = self.parse(adjective)
            if "Lemma" in features:
                del(features["Lemma"])
            adjectiveNode.features.update(features)
            
            # generate the top node and add to the graph
            propNode = PropNode.init(features={"relative":temp_t.relative_adj},
                                     index = copulaIndex,
                                     valid=True,
                                     parent_relation = adjective.parent_relation)
            self.gr.add_node(propNode)
            
            if propAsHead:
                topNode = propNode
            
            #add labeled edges
            self.gr.add_edge(edge=(subjectNode,propNode),
                             label="")
            self.gr.add_edge(edge=(propNode,adjectiveNode),
                             label="")
            
            
        return topNode


    
class appendix_types:
    def __init__(self):
        self.d = {}
    def add(self,obj):
        self._update(obj, add=+1)
    def getSet(self):
        return set([k for k in self.d.keys() if self.d[k]>0])
    def union(self,other):
        for k in other.d:
            self._update(obj=k, add=other.d[k])
            
    def remove(self,obj):
        self._update(obj, add=-1)
    def _update(self,obj,add):
        if obj not in self.d:
            self.d[obj] = 0
        self.d[obj]+=add
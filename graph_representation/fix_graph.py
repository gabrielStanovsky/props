from graph_representation.node import APPOSITION, isApposition, CopularNode,\
    addSymmetricPropogation, isConjunction, isProp, isCondition, isPreposition,\
    isAdverb, isPossessive, EXISTENSIAL, COND, isTime, TimeNode, isLocation,\
    LocationNode, join, isCopular, isRcmodProp, isDefinite, PREP
from graph_representation.graph_utils import find_nodes, duplicate_node, sort_nodes_topologically,\
    sister_nodes, is_following, reattch, duplicate_component, deref,\
    fixPossessor, find_edges, findChain, duplicateEdge, delete_component,\
    isRCmod, get_min_max_span
from graph_representation.parse_graph import POSSESSOR_LABEL,\
    APPENDIX_EXISTENSIALS, APPENDIX_RANGE, appendix_types, APPENDIX_LOCATION,\
    FIRST_ENTITY_LABEL, SECOND_ENTITY_LABEL
from dependency_tree.definitions import EXPL_LABEL, SUBJ_LABEL,\
    subject_dependencies, SOURCE_LABEL, contractions, definite_label,\
    clausal_complements, object_dependencies
from graph_representation import word, node
from graph_representation.node import Node
from graph_representation.word import Word
from dependency_tree.tree import double_filter
from constituency_tree.my_definitions import any_in

class FixGraph:
    """
    class to bunch together all function of conversion from "almost graph" to a valid graph representation
    Mainly in order to store the graph as a member which all these functions can edit.   
    """
    
    def __init__(self,graph):
        # maintain an appendix for easier browsing
        self.types = appendix_types()
        self.gr = graph
        self.applyGeneralTransformations()
        self.fixExistensials()
        self.fixPossesive()
        self.fixApposition()
        self.fixProps()
    
    
    def applyGeneralTransformations(self):
        """
        Apply general transformations on the graph in clousre mode:
        1. prop followed by cond -> cond becomes son of prop
        2. prop followed by prep -> prep becomes son of prop
        3. adv followed by prop -> adv becomes son of prop
        4. collapse cond-that
        5. collapse conjunctions (when conjunction is headed by another conjunction
        6. able -> xcomp -> predicate ===> predicate(able)
        7. time -> time ===> time
        8. time preposition -> (time or location) ===> time / location
        9. prop-> conj -> elms  ---> prop-> elms
        10. detect ranges (location, times)
        11. reduce locations with more than one child
        12. reduce locations which are headed by prop
        13. reduce prop in cases of prop -> predicate
        14. reduce prop in cases of be->prop 
        15. (acomp) reduce a predicate who is modified by a feature and has a single, sujbect, negigbour 
        16. reduce node <-> prop
        17. reduce cases of sources pointing to contractions
        """
        
        def inner():
            change = False
            # 1,2
            nodes = find_nodes(self.gr, isCondition)
            nodes.extend(find_nodes(self.gr, isPreposition))
            for curNode in nodes:
                sisterNodes = sister_nodes(graph=self.gr, node=curNode)
                for sisterNode in sisterNodes:
                    if isProp(sisterNode) and is_following(graph=self.gr,
                                                           node1=sisterNode,
                                                           node2=curNode):
                        reattch(graph=self.gr, 
                                node=curNode, 
                                new_father=sisterNode)
                        return True
                        break
            # 3
            nodes = find_nodes(self.gr, isAdverb)
            for curNode in nodes:
                sisterNodes = sister_nodes(graph=self.gr, node=curNode)
                for sisterNode in sisterNodes:
                    if isProp(sisterNode) and is_following(graph=self.gr,
                                                           node1=curNode,
                                                           node2=sisterNode):
                        reattch(graph=self.gr, 
                                node=curNode, 
                                new_father=sisterNode)
                        return True
                        break
                    
            #4
            nodes = find_nodes(self.gr,
                               lambda n:isCondition(n) and n.text[0].word == "{0}-{1}".format(COND,'that'))
            for curNode in nodes:
                curFathers = self.gr.incidents(curNode)
                curChildren = self.gr.neighbors(curNode)
                for curFather in curFathers:
                    for curChild in curChildren:
                        self.gr.add_edge(edge = (curFather,curChild),
                                         label = "that")
                self.gr.del_node(curNode)
                change = True
            
            #5
            filterFunc = lambda n:isConjunction(n) and len(self.gr.incidents(n)) == 1 and isConjunction(self.gr.incidents(n)[0]) and (n.conjType  == self.gr.incidents(n)[0].conjType) #TODO: efficiency - multiple calls to incidents and a lot of deref
            nodes = find_nodes(self.gr,filterFunc)
                               
            for curNode in nodes:
                curFather = self.gr.incidents(curNode)[0]
                for curChild in self.gr.neighbors(curNode):
                    self.gr.add_edge((curFather,curChild))
                self.gr.del_node(curNode)
                change = True 
                
            #6
            nodes = find_nodes(self.gr,
                               lambda n:len(n.text)==1 and n.text[0].word == "able")
            for curNode in nodes:
                curFathers = self.gr.incidents(curNode)
                if len(curFathers)==1:
                    curChildren = self.gr.neighbors(curNode)
                    if len(curChildren) ==1:
                        child = curChildren[0]
                        if child.isPredicate and (self.gr.edge_label((curNode,child))=="xcomp"):
                            father = curFathers[0]
                            self.gr.add_edge(edge=(father,child),
                                             label=self.gr.edge_label((father,curNode)))
                            child.features["Modal"]={"Value":['able']} #TODO: is this maybe overrun previous modals?
                            self.gr.del_node(curNode)
                            change=True
            #7
            edges = find_edges(self.gr,
                               lambda (u,v):isTime(u)and isTime(v) and len(self.gr.neighbors(u))==1)
            for curFather,curSon in edges:
                for curNode in self.gr.neighbors(curSon):
                    self.gr.add_edge(edge=(curFather,curNode),
                                     label = self.gr.edge_label((curSon,curNode)))
                self.gr.del_node(curSon)
                return True
            
            #8
            edges = find_edges(self.gr,
                               lambda (u,v):(isTime(v) or isLocation(v)) and isPreposition(u) and u.is_time_prep())
            
            for prepNode,timeNode in edges:
                if (len(self.gr.neighbors(prepNode))==1):
                    # time node is only son - attach time to all of prep incidents
                    for curFather in self.gr.incidents(prepNode):
                        self.gr.add_edge(edge=(curFather,timeNode),
                                         label = self.gr.edge_label((curFather,prepNode)))
                    self.gr.del_node(prepNode)
                    change=True
                    
            #9
            conjNodes = find_nodes(self.gr, lambda n: isConjunction(n) and n.conjType.lower() == "and")
            for conjNode in conjNodes:
                curParents = []
                curChildren = self.gr.neighbors(conjNode)
                for curChild in curChildren:
                    curParents.extend([parent for parent in self.gr.incidents(curChild) if parent != conjNode])
                
                if len(curParents)==1:
                    parent = curParents[0]
                    if isProp(parent):
                        # found a prop->conj construction 
                        # connect all prop to parent of conj and remove the conj node
                        for child in curChildren:
                            if not (parent,child) in self.gr.edges():
                                self.gr.add_edge(edge = (parent,child))
                        self.gr.del_node(conjNode)
                        change = True
                        
                    
            
            #10
            change = change or self.fixRanges()
            
            #11
            edges = find_edges(self.gr,
                               lambda (u,v):self.gr.edge_label((u,v))=="loc" and len(self.gr.neighbors(u))>1)
            
            for topNode,loc in edges:
                for curNeigbor in self.gr.neighbors(topNode):
                    if curNeigbor != loc:
                        duplicateEdge(graph=self.gr, orig=(topNode,curNeigbor), new=(loc,curNeigbor))
                for curFather in self.gr.incidents(topNode):
                    duplicateEdge(graph=self.gr, orig=(curFather,topNode), new=(curFather,loc))
                self.gr.del_node(topNode)
                self.types.remove(APPENDIX_LOCATION)
                change=True
                    
            
            #12
            edges = find_edges(graph=self.gr, 
                               filterFunc = lambda (u,v): isProp(u) and isLocation(v))
            
            for _,locNode in edges:
                for curFather in self.gr.incidents(locNode):
                    for curNeighbour in self.gr.neighbors(locNode):
                        duplicateEdge(graph=self.gr, orig=(locNode,curNeighbour), new=(curFather,curNeighbour))
                self.gr.del_node(locNode)
                self.types.remove(APPENDIX_LOCATION)
                change=True
                
            #13
            edges = find_edges(graph=self.gr, 
                               filterFunc = lambda (u,v): isProp(u) and v.isPredicate and (len(self.gr.neighbors(v)) ==0) and (len(self.gr.incidents(u)) ==1) and (len(self.gr.neighbors(u)) ==1))
            
            for propNode,predNode in edges:
                change = True
                curFather = self.gr.incidents(propNode)[0]
                if not isApposition(curFather):
                    jointNode = node.join(node1=curFather, 
                                          node2=predNode, 
                                          gr=self.gr)
                    curFather.text = jointNode.text
                    self.gr.del_nodes([propNode,predNode])
                else:
                    self.gr.del_node(propNode)
                    self.gr.add_edge((predNode,curFather))
                    for curIncident in self.gr.incidents(curFather):
                        duplicateEdge(graph=self.gr, 
                                      orig=(curIncident,curFather), 
                                      new=(curIncident,predNode))
                        self.gr.del_edge((curIncident,curFather))
                        
                        
            #14
            propNodes = find_nodes(self.gr, lambda n:isProp(n) and len(self.gr.incidents(n))==1)
            for propNode in propNodes:
                curFather = self.gr.incidents(propNode)[0]
                if ((len(curFather.str)==1) and (not isCopular(curFather)) and (curFather.str[0].word == "be" or curFather.str[0].word in contractions)) or ((isProp(curFather) or isRcmodProp(curFather)) and len(self.gr.neighbors(curFather))==1):
                    if len(self.gr.incidents(curFather))==1:                    
                        curAncestor = self.gr.incidents(curFather)[0]
                        duplicateEdge(graph=self.gr,
                                      orig=(curAncestor,curFather), 
                                      new=(curAncestor,propNode))
                        self.gr.del_node(curFather)
                        # this node no longer describes the "be" relation
                        propNode.parent_relation = ''
                        return True
            
            #15
            edges = find_edges(graph=self.gr, 
                               filterFunc = lambda (u,v): isProp(v) and (v.parent_relation == "acomp") and len(self.gr.neighbors(v))==1 and u.isPredicate)
            
            for pred, prop in edges:
                acompNode = self.gr.neighbors(prop)[0]
                duplicateEdge(graph=self.gr, orig=(pred,prop), new=(pred,acompNode),
                              newLabel = "modifier")
                self.gr.del_node(prop) # TODO: could there be others connected to it?
                newPred = node.join(pred,acompNode,self.gr)
                newPred.isPredicate =True
                self.gr.add_node(newPred)
                for neigbour in self.gr.neighbors(pred):
                    duplicateEdge(graph=self.gr, orig=(pred,neigbour), new=(newPred,neigbour))
                
                for curFather in self.gr.incidents(pred):
                    duplicateEdge(graph=self.gr, orig=(curFather,pred), new=(curFather,newPred))
                
                if len(self.gr.neighbors(acompNode))==0:
                    self.gr.del_node(acompNode)
                    
                self.gr.del_node(pred)
#                 newPred.features["debug"] =True #TODO: remove this
                self.types.add("ACOMP")
                return True
            
            #16
            edges = find_edges(graph=self.gr,
                               filterFunc = lambda (u,v): (isProp(v) or isRcmodProp(v)) and (u in self.gr.neighbors(v)))
            
            for _,v in edges:
                if (len(self.gr.neighbors(v))==1):
                    self.gr.del_node(v)
                    return True
            
            #17
            edges = find_edges(graph=self.gr,
                               filterFunc = lambda (u,v): self.gr.edge_label((u,v))==SOURCE_LABEL and (len(self.gr.neighbors(v))==0))
            for _,v in edges:
                curStr = " ".join([w.word for w in v.text])
                if curStr in contractions:
                    self.gr.del_node(v)
                    return True
                        
            #18 - verbal complements
            edges = find_edges(graph=self.gr,
                               filterFunc = lambda (u,v): self.gr.edge_label((u,v))=='ccomp' and u.isPredicate)
            for u,v in edges:
                self.gr.del_edge((u,v))
                self.gr.add_edge(edge=(u,v),
                                 label = 'dobj')
                v.features["debug"] =True
                self.types.add("DEBUG")
                return True
                    
            return change
        
                
        
        
        ret = True
        while ret:
            ret = inner()
        return ret
    
    
    
    
    
    def fixRanges(self):
        rangeFuncList = [lambda n:(isPreposition(n) and n.prepType == "from" and len(self.gr.neighbors(n))==1),
                         lambda n:((isTime(n) or isLocation(n)) and len(self.gr.neighbors(n))==2),
                         lambda n:(isPreposition(n) and n.prepType == "to" and len(self.gr.neighbors(n))==1),
                         lambda n:((isTime(n) or isLocation(n)) and len(self.gr.neighbors(n))==1)]
        ls = findChain(self.gr, rangeFuncList)
        if not ls:
            return False
        
        [fromNode,start,toNode,end] = ls
        startNode = [n for n in self.gr.neighbors(start) if not isPreposition(n)][0]
        endNode = self.gr.neighbors(end)[0]
        if isTime(start):
            rangeNode = TimeNode.init(features={"Range":True})
        elif isLocation(start):
            rangeNode = LocationNode.init(features={"Range":True})
            
        self.gr.add_node(rangeNode)
        if isTime(start):
            sonNode = Node(isPredicate=False,
                           text = startNode.text + [Word(index=toNode.text[0].index,word="to")]+ endNode.text,
                           features = {'Time Value':"-".join([startNode.features['Time Value'],
                                                              endNode.features['Time Value']])},
                           valid=True)
        elif isLocation(start):
            sonNode = Node(isPredicate=False,
                           text = startNode.text + [Word(index=toNode.text[0].index,word="to")]+ endNode.text,
                           features = {},
                           valid=True)
        self.gr.add_node(sonNode)
        self.gr.add_edge((rangeNode,sonNode))
        for curFather in self.gr.incidents(fromNode):
            duplicateEdge(graph=self.gr, 
                          orig=(curFather,fromNode), 
                          new=(curFather,rangeNode))
        
        delete_component(graph=self.gr, node=fromNode)
        self.types.add(APPENDIX_RANGE)
        return True
    
    def fixExistensials(self):
        """ 
        Generate existensials structure
        """
        explEdges = find_edges(graph = self.gr, 
                               filterFunc = lambda edge: self.gr.edge_label(edge) == EXPL_LABEL)
        for (topNode,expl) in explEdges:
            subjNodes = deref(graph=self.gr, node=topNode, rel= subject_dependencies)
            if len(subjNodes)!=1:
                continue
            self.types.add(APPENDIX_EXISTENSIALS)
            self.gr.del_node(expl)
            subjNode = subjNodes[0]
            for curNeigbour in [n for n in self.gr.neighbors(topNode) if n != subjNode]:
                self.gr.add_edge(edge = (subjNode,curNeigbour),
                                 label = self.gr.edge_label((topNode,curNeigbour)))
                self.gr.del_edge((topNode,curNeigbour))
            topNode.text[0].word = EXISTENSIAL
            topNode.features = {}
    
    def fixPossesive(self):
        """
        fix phrasing in possessives, such as "its -> it" "her -> she" "his -> he", etc.
        """
        possNodes = find_nodes(self.gr, isPossessive)
        for possNode in possNodes:
            possessor = deref(graph=self.gr, node = possNode, rel = POSSESSOR_LABEL)[0]
            fixPossessor(possessor)
                
    def fixApposition(self):
        """ 
        remove apposition nodes, and change to our format
        """
        def inner(curNode,children,relation):
            curNode.dups = [duplicate_node(graph=self.gr,node=curNode,connectToNeighbours=True) for _ in children]
            for childIndex,child in enumerate(children):
                self.gr.add_edge(edge = (curNode.dups[childIndex],child),
                                 label = relation)
            parents = self.gr.incidents(curNode)
            for parent in parents:
                if not hasattr(parent,'isDuplicated'): #TODO: efficiency
                    if hasattr(parent,'dups'):        #TODO: efficiency
                        for curParentDupInd,curParentDup in enumerate(parent.dups): # cycle detected - we already visited this parent, don't enter recursion
                            self.gr.add_edge(edge  = (curParentDup,curNode.dups[curParentDupInd]),
                                             label = self.gr.edge_label((parent,curNode)))
                    else:
                        inner(curNode = parent,
                              children = curNode.dups,
                              relation = self.gr.edge_label((parent,curNode)))
            
            self.gr.del_node(curNode)
            
        # find apposition nodes in topological ordering 
        apposNodes = sort_nodes_topologically(self.gr,find_nodes(self.gr, isApposition))
        
        for apposNode in apposNodes:
            # for each apposition node
            entities = [n for n in self.gr.neighbors(apposNode) if self.gr.edge_label((apposNode,n)) in [FIRST_ENTITY_LABEL,SECOND_ENTITY_LABEL]] 
            # move rcmod construction to the apposition node
            for entInd,ent in enumerate(entities):
                isEntRCmod = isRCmod(graph=self.gr,node=ent) 
                if isEntRCmod:
                #if hasattr(ent,'rcmod'): #TODO: efficiency
                    secondEntity = entities[entInd-1]
                    propNode,relClause = isEntRCmod
                    dupProp = duplicate_node(graph=self.gr, node=propNode, connectToNeighbours=False)
                    dupRelClause = duplicate_node(graph=self.gr, node=relClause, connectToNeighbours=False)
                    self.gr.add_edge((secondEntity,dupProp))
                    self.gr.add_edge((dupProp,dupRelClause))
                    self.gr.add_edge(edge=(dupRelClause,secondEntity),
                                     label=self.gr.edge_label((relClause,ent)))
                    
                    for curNeigbour in self.gr.neighbors(relClause):
                        if curNeigbour != ent:
                            topNode = duplicate_component(graph=self.gr, node=curNeigbour)
                            self.gr.add_edge(edge=(dupRelClause,topNode),
                                             label=self.gr.edge_label((relClause,curNeigbour)))
            
            # get his non-entities children
            # and connect to entities 
            children = [c for c in self.gr.neighbors(apposNode) if c not in entities]
            for child in children:
                for ent in entities:
                    self.gr.add_edge(edge=(ent,child),
                                     label = self.gr.edge_label((apposNode,child)))
                # remove connection to appos node
                self.gr.del_edge(edge=(apposNode,child))    
            
            
            # connect entities of apposition to the copular node    
            # and copy all propagation from appos node to its entities
            copNode = CopularNode.init(index = apposNode.text[0].index,     # create a copular node to replace it
                                  features = apposNode.features,
                                  valid=True)
            self.gr.add_node(copNode) # add it to graph
            
            for ent in entities:
                self.gr.add_edge(edge = (copNode,ent),
                                 label = self.gr.edge_label((apposNode,ent)))
                for curNode in apposNode.propagateTo:
                    addSymmetricPropogation(ent,curNode)
                
            
            # deal with parent of apposition
            for parent in self.gr.incidents(apposNode):
                inner(curNode = parent,
                      children = entities,
                      relation = self.gr.edge_label((parent,apposNode)))
                
            # finally - remove the apposition                
            self.gr.del_node(apposNode)
            
    def fixProps(self):
        """
        Fix cases of conjunction of properties in indefinite nominals 
        """
        
        edges = find_edges(graph = self.gr, 
                           filterFunc = lambda (u,v): (not isDefinite(u)) and (isProp(v)or isRcmodProp(v)) and (not v.is_prenominal()))
        
        for counter,(u,v) in enumerate(sorted(edges,key= lambda (_,propNode):get_min_max_span(self.gr,propNode)[0])):
            curLabel = self.gr.edge_label((u,v))
            self.gr.del_edge((u,v))
            self.gr.add_edge(edge =(u,v),
                             label = ";".join([curLabel,str(counter+1)]))
            
            
        
        
            
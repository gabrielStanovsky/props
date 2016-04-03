from graph_representation.node import isProp, isTime
class Propagate:
    """
    class to bunch together all function of propagation on a digraph
    Mainly in order to store the graph as a member which all these functions can edit.   
    """
    def __init__(self,graph):
        self.gr = graph
        self.applyPropagation()
        
    def applyPropagation(self):
        """
        Apply closure propagation algorithms on the graph
        """
        change = True
        while change:
            change = self.propogateFeatures()
    
    def propogateFeatures(self):
        """
        handle propagating features between nodes of the graph
        
        @rtype  bool
        @return True iff this function has changed the graph in some way 
        """
        ret = False
        for curNode in self.gr.nodes():
            # for each node in the graph
            curNodeNeigbours = self.gr.neighbors(curNode)
            for curPropogateNode in curNode.propagateTo:
                # for each of its propgated nodes
                curPropogateNodeNeigboursIds = [cpn.uid for cpn in self.gr.neighbors(curPropogateNode)]
                for curNeigbour in curNodeNeigbours:
                    if isProp(curNeigbour) or isTime(curNeigbour):
                        # for each *prop* neigbour
                        if curNeigbour.uid not in curPropogateNodeNeigboursIds:
                            # if its not a neigbour of propogated node - add it
                            self.gr.add_edge(edge=(curPropogateNode,curNeigbour), 
                                             label=self.gr.edge_label((curNode,curNeigbour)))
                            # mark that a change was made to the graph
                            ret = True
        return ret
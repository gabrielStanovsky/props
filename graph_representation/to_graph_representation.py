from subprocess import call
from graph_representation.parse_graph import ParseGraph
from graph_representation.propagate import Propagate
from graph_representation.fix_graph import FixGraph
import file_handling
import pygraph.readwrite.dot
from graph_representation.graph_wrapper import GraphWrapper
from graph_representation.word import Word
from graph_representation.node import Node, isCondition
import graph_representation.newNode
from graph_representation import newNode
from proposition_structure.syntactic_item import get_verbal_features
from copy import copy



class GraphRepresentation:
    """
    class to bunch together all function of conversion.
    Mainly in order to store the graph as a member which all these functions can edit.   
    """

    def __init__(self,t,locationAnnotator):
        """
        initialize a GraphRepresentation class, followed by converting a tree to to graph

        @type  t: DepTree
        @param tree: syntactic tree to be converted
        
        
        @type gr: digraph
        @var  gr: the graph representing t
        """
        self.depTree          = t
        if not ban(t):
            self.originalSentence = t.get_original_sentence()
            self.gTag             = ParseGraph(t,locationAnnotator) # an almost graph
            self.g0               = FixGraph(self.gTag.gr)         # a valid graph
            self.propogatedGraph  = Propagate(self.g0.gr)          # a fully propagated graph
            self.gr = self.propogatedGraph.gr
#             self.gr = self.g0.gr
        
            self.gr.tokens        = self.originalSentence.split()
            self.types= self.gTag.types
            self.types.union(self.g0.types)
        
        else:
            self.gTag = False
        
        
    
    def draw(self):
        """ 
        draw self on the screen
        """
        self.gr.draw()
        
    def drawToFile(self,filename,filetype):
        """ 
        Saves a graphic filename of this graph
        
        @type  filename string
        @param name of file in which to write the output, without extension
        
        @type  filetype string
        @param the type of file [png,jpg,...] - will be passed to dot 
        """
        
        self.gr.writeToDot(filename=filename+".dot",
                           writeLabel = (filetype=="svg"))
        call("dot -T{1} {0}.dot -o {0}.{1}".format(filename,filetype).split())


def parseGraph(t):
    """
    Utility function to obtain a graph from a tree in a single line
    
    @type  t: Tree
    @param t: tree to be converted to graph
    
    @rtype: digraph
    @return the graph representing the Tree t
    """
    
    pg = GraphRepresentation(t)
    return pg.gr
    


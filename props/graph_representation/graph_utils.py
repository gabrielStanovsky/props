from pygraph.algorithms.sorting import topological_sorting
from pygraph.classes.digraph import digraph
# import graph_representation.node
import subprocess, math, re, nltk
from pygraph.algorithms.accessibility import accessibility
from props.graph_representation.word import NO_INDEX, Word, strip_punctuations
from pygraph.algorithms.traversal import traversal
from pygraph.algorithms.minmax import minimal_spanning_tree, shortest_path
import cgi
# from graph_representation.node import isRcmodProp
import time
# from graph_representation.node import Node
from props.graph_representation import newNode
from operator import itemgetter
import logging

def accessibility_wo_self(graph):
    ret = accessibility(graph)
    for k in ret:
        ret[k].remove(k)
    return ret

# def isRCmod(graph, node):
#     ns = graph.neighbors(node)
#     for neigbour in ns:
#         if isRcmodProp(neigbour):
#             propNs = graph.neighbors(neigbour) 
#             if len(propNs) == 1:
#                 return neigbour, propNs[0]
#     return False

def duplicate_node(graph, node, connectToNeighbours):
    """
    Duplicates node in a graph, *not* including all ingoing and outgoing edges
    
    @type  graph: GraphWrapper
    @param graph: the graph in which to duplicate the node
    
    @type  node: graph_representation.node.Node
    @param node: node to duplicate
    
    @type  connectToNeighbours: boolean
    @param connectToNeighbours: indicating wheter the duplicated node should be connected to the
                                neigbours of the original node
    
    @rtype  Node
    @return the duplicated node
    """
    dupNode = node.copy()
    dupNode.isDuplicated = True
    graph.add_node(dupNode)
    
    if connectToNeighbours:
        for curNeighbour in graph.neighbors(node):
            graph.add_edge((dupNode, curNeighbour), graph.edge_label((node, curNeighbour)))
    
    return dupNode


def get_node_dic(graph, node):
    d = {}
    for neighbor in graph.neighbors(node):
        curLabel = graph.edge_label((node, neighbor))
        if curLabel not in d:
            d[curLabel] = []
        d[curLabel].append(neighbor)
    return d

def duplicateEdge(graph, orig, new, newLabel=""):
    """
    adds a new edge, duplicating the label of the original one
    """
    label = graph.edge_label(orig)
    if not label:
        label = newLabel
        
    graph.add_edge(edge=new,
                   label=label)


def findChain(graph, func_ls):
    """
    find a chain of connected in the graph and corresponding to func_ls
    Returns one arbitrary chain which matches all functions.
    """
    def inner(nodes, func_ls):
        if (len(func_ls) == 0):
            return []
        remaining_nodes = filter(func_ls[0], nodes)
        for node in remaining_nodes:
            curAns = inner(graph.neighbors(node), func_ls[1:])
            if (len(curAns) == len(func_ls) - 1):
                return [node] + curAns
        return []
            
    return inner(nodes=graph.nodes(),
                 func_ls=func_ls) 


def delete_component(graph, node):
    """
    deletes component in a graph
    
    @type  graph: GraphWrapper
    @param graph: the graph in which to delete the component
    
    @type  node: graph_representation.node.Node
    @param node: node which roots the component to be deleted
    """
    
    nodes = minimal_spanning_tree(graph=graph,
                                  root=node)
    
    for node in nodes:
        graph.del_node(node)



def component_to_string(graph, node):
    """
    get a textual value of a component in a graph
    
    @type  graph: GraphWrapper
    @param graph: the graph in which to delete the component
    
    @type  node: graph_representation.node.Node
    @param node: node which roots the component
    """
    
    nodes = minimal_spanning_tree(graph=graph,
                                  root=node)
    
    texts = []
    for node in nodes:
        texts.extend([w for w in node.get_text(graph) if w.index != NO_INDEX])
    

    chars = '\'\"-,.:;!? '    
    return " ".join([w.word for w in sorted(texts, key=lambda w:w.index)]).rstrip(chars).lstrip(chars)



    

def duplicate_component(graph, node):
    """
    Duplicates component in a graph
    
    @type  graph: GraphWrapper
    @param graph: the graph in which to duplicate the component
    
    @type  node: graph_representation.node.Node
    @param node: node which roots the component to be duplicated
    
    @rtype  Node
    @return the duplicated node of the input node, which roots the duplicated component
    """
    nodesMap = {}
    nodes = minimal_spanning_tree(graph=graph,
                                  root=node)
    for curNode in nodes:
        dupNode = duplicate_node(graph=graph,
                                 node=curNode,
                                 connectToNeighbours=False)
        nodesMap[curNode.uid] = dupNode
    
    for curNode in nodes:
        curDupNode = nodesMap[curNode.uid]
        for curNeighbour in graph.neighbors(curNode):
            curDupNeighbour = nodesMap[curNeighbour.uid]
            graph.add_edge(edge=(curDupNode, curDupNeighbour),
                           label=graph.edge_label((curNode, curNeighbour)))
    
    return nodesMap[node.uid]


def find_nodes(graph, filterFunc):
    """
    Find nodes in graph that match a filter function
    
    @type  graph: graph_wrapper
    @param graph: the graph in which to find nodes
    
    @type  filterFunc: lambda(Node):bool
    @param filterFunc: function that receives a node and returns true if you want to include it in the return list
    
    @rtype list(Node)
    @param list of Node objects matching filter func.
    """
    return filter(filterFunc, graph.nodes())


def find_edges(graph, filterFunc):
    """
    Find edges in graph that match a filter function
    
    @type  graph: graph_wrapper
    @param graph: the graph in which to find edges
    
    @type  filterFunc: lambda(edge):bool
    @param filterFunc: function that receives an edge and returns true if you want to include it in the return list
    
    @rtype list(edges)
    @param list of edges matching filter func. 
    """
    return filter(filterFunc, graph.edges())



def join(graph, nodeLs):
    """
    Adds to graph a node combined of nodes specified in nodeLs, any child of them
    will be his child. No parent will be attached to it by this function.
    
    @type  graph: graph_wrapper
    @param graph: the graph in which to create the new node
    
    @type  nodeLs: list
    @param nodeLs: list of Nodes to be joined
    
    @rtype Node
    @return The combined node
    """
    # combine node features and add to graph
    combinedNode = reduce(graph_representation.node.join, nodeLs) 
    graph.add_node(combinedNode)
    
    # add all children from both nodes as children of the combined node
    # TODO: need to handle cases where node1 and node2 are neighbors of the same node, currently 
    # will raise exception from the graph when adding an already existing edge
    for curNode in nodeLs:
        if curNode.uid in graph.nodesMap:  # allow for nodes which aren't placed in the graph to join
            for child in graph.neighbors(curNode):
                graph.add_edge((combinedNode, child), label=graph.edge_label((curNode, child)))
        
    return combinedNode


def generate_possessive_top_node(graph, nodeLs):
    """
    Generate a possessive top node, from relevant node list.
    Takes into account cases like appositions, and other "invalid" nodes.
    @todo: Here should implement the decision on where to cut an NP. For instance see sentence #172
    
    @type  graph: graph_wrapper.GraphWrapper
    @param graph: a graph in which the nodes reside
    
    @type  nodeLs: list [node]
    @param nodeLs: a list of nodes from which to generate the top nodes
    
    @rtype:  Node
    @return: the top node for a possessive construction
    """
    
    ls = []
    # extend apposition node to their elements
    for node in nodeLs:
        if graph_representation.node.isApposition(node):
            ls.extend(graph.neighbors(node))
            
        else:
            ls.append(node)
    
    topNode = ls[0]
    for curNode in ls[1:]:
        topNode = graph_representation.node.join(topNode, curNode, graph)
    return topNode





def sort_nodes_topologically(graph, nodeLs):
    """
    Get a topological sort of a subset of the nodes of a graph
    
    @type  graph: graph_wrapper.GraphWrapper
    @param graph: a graph in which the nodes reside

    @type  nodeLs: list [node]
    @param nodeLs: a list of nodes from which to generate sorting. nodes must not be mutually accessive!
    
    @rtype:  list [node]
    @return: topological sort of the nodes
    """
    # uid_dic = dict([(node.uid,node) for node in nodeLs])
    # helperNodes = uid_dic.keys()
    helperGraph = graph.__class__(originalSentence="")  # TODO: efficiency - this is done this way to avoid circular dependency
    helperGraph.add_nodes(nodeLs)
    acc = accessibility(graph)
    
    for node1 in nodeLs:
            for node2 in acc[node1]:
                if node2 in nodeLs:
                    if node1.uid != node2.uid:  # TODO: efficiency 
                        helperGraph.add_edge((node1, node2))
    
    sorted_nodes = topological_sorting(helperGraph)
    return sorted_nodes


def get_min_max_span(graph, node):
    """
    Get minimum and maximum indices covered by the subgraph rooted at a specific node
    
    @type  graph: graph_wrapper.GraphWrapper
    @param graph: a graph in which the node reside

    @type  node: node
    @param node: root of the given subgraph
    
    @rtype:  tuple [int]
    @return: (min,max) 
    """
    
    minInd = NO_INDEX
    maxInd = NO_INDEX
    
    for curNode in traversal(graph, node, 'pre'):
        curMin = curNode.minIndex()
        curMax = curNode.maxIndex()
        
        maxInd = max(maxInd, curMax)
        if curMin != NO_INDEX:
            if minInd == NO_INDEX:
                minInd = curMin
            else:
                minInd = min(minInd, curMin)
            
    return (minInd, maxInd)


def sister_nodes(graph, node):
    """
    Get sister nodes of a specified node (including the node itself)
    
    @type  graph: graph_wrapper.GraphWrapper
    @param graph: a graph in which the node reside

    @type  node: node
    @param node: node for which to find sister nodes
    
    @rtype:  list [node]
    @return: all sister nodes 
    """
    
    ret = set()
    for curIncident in graph.incidents(node):
        ret = set.union(ret, set(graph.neighbors(curIncident)))
    return ret

def is_following(graph, node1, node2):
    """
    is node1 immediately followed by node2?
    """
    node1_max = get_min_max_span(graph, node1)[1]
    node2_min = get_min_max_span(graph, node2)[0]
    return (node1_max + 1 == node2_min)

def immediate_sister(graph, node1, node2):
    """
    is node2 an immediate sister of node1?
    """
    
    return (node2 in sister_nodes(graph, node1) and is_following(graph, node1, node2))

def reattch(graph, node, new_father, label=""):
    """
    change graph formation so that new_father becomes the only father of node
    
    @type  graph: graph_wrapper.GraphWrapper
    @param graph: a graph in which the node reside

    """
    
    for curFather in graph.incidents(node):
        graph.del_edge(edge=(curFather, node))
    
    graph.add_edge(edge=(new_father, node),
                   label=label)
     
    
def deref(graph, node, rel):
    """
    get all neighboring nodes of "node" which are connected through rel (which can either be a single relation or a list of relations)
    useful for traversing relations in the graph.
    """
    
    neighbors = graph.neighbors(node)
    if isinstance(rel, list):
        ret = []
        for curRel in rel:
            ret.extend([n for n in neighbors if graph.edge_label((node, n)) == curRel])  # TODO: efficiency
    else:
        ret = [n for n in neighbors if graph.edge_label((node, n)) == rel]
    return ret


def find_node_by_index_range(graph, start, end):
    """
    find a node which covers the span
    if no such node exists returns False
    """
    for node in graph.nodes():
        indices = [w.index for w in node.str if w.index != NO_INDEX]
        if indices:
            if (start >= min(indices)) and (end <= max(indices)):
                return node
    return False

def to_undirected(graph):
    ret = graph.__class__("")
    ret.add_nodes(graph.nodes())
    for u, v in graph.edges():
        if not(ret.has_edge((u,v))):
            ret.add_edge(edge=(u, v),
                         label=graph.edge_label((u, v)))
        if not(ret.has_edge((v,u))):
            ret.add_edge(edge=(v, u),
                         label=graph.edge_label((u, v)))
    return ret
    

def shortest_distance(graph, node1, node2):
    """
    minimum distance between two nodes in the graph
    """
    undirected = to_undirected(graph)
    _, d = shortest_path(graph=undirected, source=node1)
    if node2 not in d:
        return -1
    return d[node2]

def find_top_of_component(graph, source_node):
    """
    Find the top node of the connected component in which source_node resides.
    Since this graph may contain cycles - we go "up" the graph, as long as we don't revisit nodes
    """
    _, d = shortest_path(reverse_graph_edges(graph), # Reverse graph to go up
                         source = source_node)
    return max(d.iteritems(),
               key = itemgetter(1))[0] # Returns the farthest away node

def reverse_graph_edges(graph):
    """
    Returns a reversed version of the input graph.
    I.e., for each edge (u, v) in graph, there will be an edge (v, u) in the
    returned graph.
    The labels aren't changed.
    """
    ret_graph = digraph()

    # Add all nodes to the return graph
    for node in graph.nodes():
        ret_graph.add_node(node)

    # Add reveresed edges to the returned graph
    for (u, v) in graph.edges():
        ret_graph.add_edge((v, u),
                           label = graph.edge_label((u, v)))

    return ret_graph

def merge_nodes(gr, node1, node2):
    if (gr.has_edge((node1, node2))):
        gr.del_edge((node1, node2))
    else:
        gr.del_edge((node2, node1))
        
    new = newNode.join(node1, node2, gr)
    for curNode in [node1, node2]:
        for curFather in gr.incidents(curNode):
            if (not gr.has_edge((curFather,new))):
                duplicateEdge(graph=gr,
                              orig=(curFather, curNode),
                              new=(curFather, new))
        for curNeigbour in gr.neighbors(curNode):
            if (not gr.has_edge((new,curNeigbour))):
                duplicateEdge(graph=gr,
                              orig=(curNode, curNeigbour),
                              new=(new, curNeigbour))
    gr.del_nodes([node1, node2])

def subgraph_to_string(graph,node,exclude=[]):
    nodes = [node]
    change = True
    while change:
        change=False
        for curNode in nodes:
            for curNeigbour in graph.neighbors(curNode):
                if (curNeigbour in nodes) or (curNeigbour in exclude): continue
                nodes.append(curNeigbour)
                change = True
    

#     minInd = min([n.minIndex() for n in nodes])-1
#     maxInd = max([n.maxIndex() for n in nodes])-1
#     ret = " ".join(graph.originalSentence.split(" ")[minInd:maxInd+1])
#     nodes = [n for n in minimal_spanning_tree(graph, node) if not n in exclude]
#     ret = " ".join(node.get_original_text() for node in sorted(nodes,key = lambda n: n.minIndex()))
    try:
        ret = ""
        words = []
        for n in nodes:
            words += n.surface_form
        words = list(set(words))
        ret = " ".join([w.word for w in strip_punctuations(sorted(words,key=lambda w:w.index))])+" "
    except:
        raise Exception()
#     
    
    return ret


def multi_get(d, ls):
    ret = []
    for k in ls:
        ret.extend(d.get(k, []))
    return ret        



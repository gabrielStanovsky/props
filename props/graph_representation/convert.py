from props.proposition_structure.syntactic_item import get_verbal_features
from props.graph_representation import newNode
from props.graph_representation.word import Word, NO_INDEX
from copy import copy
# from graph_representation.graph_wrapper import GraphWrapper
import cgi,time
import subprocess,math,re,os
from pygraph.algorithms.minmax import shortest_path, minimal_spanning_tree
from props.graph_representation.graph_utils import get_min_max_span, duplicateEdge,\
    find_edges
from pygraph.algorithms.accessibility import accessibility
from props.graph_representation.graph_wrapper import GraphWrapper
import props.dependency_tree
from props.dependency_tree.tree_readers import create_dep_trees_from_stream
# from graph_representation.graph_wrapper import GraphWrapper




def treeNode_to_graphNode(treeNode,gr):
    """
    @type treeNode DepTree
    """
    
    feats = get_verbal_features(treeNode)
    ret = newNode.Node(text = [Word(index=treeNode.id,
                                    word = treeNode.word)],
                       isPredicate = treeNode.is_verbal_predicate(),
                       features = feats,
                       gr = gr)
    ret.features["pos"] = treeNode.pos
    ret.original_text = copy(ret.text)
    return ret


#
#
def tree_to_graph(tree):
    """
    @type tree DepTree
    """

    HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR")+"\\"

    ret = GraphWrapper(tree[0].original_sentence,HOME_DIR)
    graphNodes = {}
    for t in tree.values():
        if t.id:
            if t.parent_relation != "erased":

                graphNodes[t.id]=treeNode_to_graphNode(t,ret)
    for t in tree.values():
        if t.id:
            curParent =t.parent.id
            if curParent:
                ret.add_edge(edge=(graphNodes[curParent],graphNodes[t.id]),
                             label = t.parent_relation)

    return ret

def collapse_graph(gr):
    # prepositions
    prep_edges = find_edges(graph=gr, filterFunc = lambda (u,v): gr.edge_label((u,v))=="prep" and gr.neighbors(v)==1)
    for u,v in prep_edges:
        pobj = gr.neighbors(v)[0]
        gr.add_edge((u,pobj),"prep_"+v.text[0].word.lower())
        gr.del_node(v)
        
    # conjunctions
    conj_edges = find_edges(graph=gr, filterFunc = lambda (u,v): gr.edge_label((u,v))=="conj" and len(u.neighbors().get("cc",[]))==1)
    toDel = []
    for u,v in conj_edges:
        cc = u.neighbors()['cc'][0]
        if len(gr.neighbors(cc))==0:
            gr.del_edge((u,v))
            gr.add_edge((u,v),"conj_"+cc.text[0].word.lower())
            toDel.append(cc)
    for n in set(toDel):
        gr.del_node(n)
    return gr
    
def convert(gr):
#     gr = tree_to_graph(tree)
    gr.types = appendix_types()
    gr.remove_aux()
    gr.merge()
    gr.fix()
    gr.do_passives()
    gr.do_existensials()
    gr.do_conditionals()
    gr.do_prop()
    gr.do_acomp()
    gr.do_poss()
    gr.do_vmod_relclause()
    gr.do_conj()
    gr.normalize_labels()
    gr.calcTopNodes()
    return gr




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
        
        
def find_node_by_string(graph,s):
    originalSentence = graph.originalSentence.split()
    words = s.split()
    startWord,endWord = words[0],words[-1]
    if (startWord in originalSentence) and (endWord in originalSentence):
        start = originalSentence.index(startWord)+1
        end  = originalSentence.index(endWord)+1
        return find_node_by_index_range(graph,start,end)
    return False 

def find_node_by_index_range(graph, start, end):
    """
    find a node which covers the span
    if no such node exists returns False
    """
#     acc = accessibility(graph)
    ret = False
    nodeSpan = -1
    for node in graph.nodes():
        if node.is_implicit():
            continue
        minInd,maxInd = get_min_max_span(graph=graph, node=node)
        if (start >= minInd) and (end <= maxInd):
            curSpan = maxInd-minInd
            if ((not ret) or (nodeSpan > curSpan)) or ((curSpan==nodeSpan) and 
                                                       list(set.intersection(set([w.index for w in node.surface_form]),
                                                                             set(range(start,end+1))))):
                ret = node
                nodeSpan = curSpan
                
    flag = bool(list(set.intersection(set([w.index for w in ret.text]),
                                      set(range(start,end+1))))) #indicates if the returned node covers the entity
    return (ret,flag)

    
#     for node in graph.nodes():
#         indices = [w.index for w in node.text if w.index != NO_INDEX]
#         if indices:
#             if (start >= min(indices)) and (end <= max(indices)):
#                 return node
#     return False
def to_undirected(graph):
    ret = graph.__class__("",graph.HOME_DIR)
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
    
#     t = minimal_spanning_tree(graph,node1)
#     if node2 not in t:
#         return -1
#     
    undirected = to_undirected(graph)
    t, d = shortest_path(graph=undirected, source=node1)
    if node2 not in d:
        return -1
    ret = [node2]
    v = node2
    while v!= node1:
        u = t[v]
        ret.extend([undirected.edge_label((u,v)),graph.has_edge((u,v)),u])
        v=u
#     return ret

    return ret



    
    


if __name__ == "__main__":
    import fileinput
    trees = dependency_tree.tree_readers.create_dep_trees_from_stream(fileinput.input(), wsjInfo_exists=False)
    for tree in trees:
	try:
	        gr = tree_to_graph(tree)
        	gr = collapse_graph(gr)
	        gr = convert(gr)
	        print gr
	except:
		pass
        gr = tree_to_graph(tree)
        gr = collapse_graph(gr)
        gr = convert(gr)
        print gr
#    f.close()

        

#     from graph_representation.annotations.manual_annotations import ManualAnnotation

#     JESSICA,GABI=(0,1)
#     USERS = {JESSICA: "C:\\Users\\user\\PycharmProjects\\propextraction\\",
#              GABI: "C:\\Users\\user\\git\\propextraction\\"}
#     USER = JESSICA
#     HOME_DIR = USERS[USER]
# 
#     from file_handling import load_depTrees_from_file,merge
#     from graph_representation.graph_wrapper import  dumpGraphsToTexFile
# 
#    # manual_annotation = ManualAnnotation(vadas=False,nombank=False,traces=True,light_verbs=False,relative_path=HOME_DIR)
#     trees = merge(HOME_DIR+"ptb_hundreds.dp",HOME_DIR+"PTB_collapsed_hundreds.dp")[:10]
#     gs = [convert(t) for t in trees]
#     print trees[0]
# 
#     dumpGraphsToTexFile(graphs= gs,graphsPerFile = 1500,appendix = {},lib=HOME_DIR+"/pdf/",outputType="html")



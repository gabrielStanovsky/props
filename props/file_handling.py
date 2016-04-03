#procedures for storing and restoring objects from files
import props.dependency_tree
import json,copy
from props.proposition_structure.syntactic_item import get_verbal_features
from props.dependency_tree.tree_readers import missing_children
from props.graph_representation import newNode
from props.graph_representation.word import Word
from props.graph_representation.graph_wrapper import GraphWrapper
from pygraph.classes.digraph import digraph

#read constituency format in file inp, convert it to dependency format and dump to file out
def save_depTrees_to_file(inp,out):
    f = open(out,'w')
    counter = 0
    dep_trees = dependency_tree.tree_readers.read_trees_file(inp)
    
    for tree in dep_trees:
        print counter
        assert(len(tree.children)==1)
        f.write(tree.children[0].to_original_format(root=True)+"\n")
        counter+=1    
    f.close()
    
# save all verbal predicates in inp, which is in PTB format, to out 
def save_verbal_predicates_to_file(inp,out):
    f = open(out,'w')
    counter = 0
    dep_trees = dependency_tree.tree_readers.read_trees_file(inp)
    
    for tree in dep_trees:
        
        for verb_subtree in tree.collect_verbal_predicates():
            print counter
            f.write(verb_subtree.to_original_format(root=True)+"\n")
            counter+=1
            
            
    f.close()
    
# load dependency trees from file inp
def load_depTrees_from_file(inp,wsjInfo_exists=True):
    f =open(inp,'r')
    ret = dependency_tree.tree_readers.create_dep_trees_from_stream(f,wsjInfo_exists)
#     f.close()
    return ret

# load dependency trees from file inp
def load_depGraphs_from_file(inp,wsjInfo_exists=False):
    HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR")+"\\"
    f =open(inp,'r')
    ret = dependency_tree.tree_readers.create_dep_graphs_from_stream(f,HOME_DIR)
    #f.close()
    return ret

def merge(treesFile,graphFile):
    trees = load_depTrees_from_file(treesFile)
    graphsFromFile = load_depGraphs_from_file(graphFile)
#     assert(len(trees)==len(graphsFromFile))
#     print "len ok"
    graphs = []
    for i,t in enumerate(trees):
        curGraph,nodesMap = graphsFromFile[i]
        curGraph.wsj_id = t[0].wsj_id
        curGraph.sent_id = t[0].sent_id
        curGraph.originalSentence = t[0].original_sentence
        curGraph.wsj_id = t[0].wsj_id
        curGraph.sent_id = t[0].sent_id
        curGraph.tree_str = "\n".join(t[0].to_original_format().split("\n")[1:])
        for node_id in nodesMap:
            int_node_id = int(node_id.split("'")[0])
            treeNode = t[int_node_id]
            child_dic = treeNode._get_child_dic()
            if 'cc' in child_dic:
                conj_type = (" ".join([cc.word for cc in sorted(child_dic['cc'],key=lambda cc:cc.id)]),[cc.id for cc in child_dic['cc']])
            else:
                conj_type = False
            graphNodes = [nodesMap[n] for n in nodesMap if n.split("'")[0] == node_id]
            for graphNode in graphNodes:
                graphNode.features = get_verbal_features(treeNode)
                if conj_type:
                    graphNode.features["conjType"] = conj_type
                graphNode.features["pos"]=treeNode.pos
                graphNode.isPredicate = treeNode.is_verbal_predicate()
#                 graphNode.original_text = copy.copy(graphNode.text)
                graphNode.original_text = treeNode.get_text()
                graphNode.surface_form += missing_children(treeNode,graphNode)
        curGraph.del_node(nodesMap['0']) # delete root
        graphs.append(curGraph)   
    return graphs


# dump a Proposition structure list into filename in json format (overwrites file content)        
def dumpPsToFile(ls,filename,append=False):
    #convert list to json format
    j = [p.toJson() for p in ls]
    #dump to file
    if append:
        f = open(filename,'a')
    else:
        f = open(filename,'w')
    json.dump(j,f)    
    f.close()
    
    
def load_prop_from_file(filename,HOME_DIR):
    fin = open(filename)
    flag = True
    ret = []
    for line in fin:
        line = line.strip("\n")
        if flag:
            curSentence = line
            flag=False
            curGraph = GraphWrapper(curSentence,HOME_DIR)
            parentsList = []
        else:
            if line:
                uid,words,pos,isPredicate,isAsserted,parents = line.split("\t")
                uid = int(uid)
                isAsserted = bool(int(isAsserted))
                text = [Word(int(index),word) for index,word in [ent.split(",") for ent in words.split(";")]]
                if isAsserted:
                    feats={"top":isAsserted}
                else:
                    feats={}
                if parents:
                    parentsList.extend([((int(index),uid),rel) for rel,index in [ent.split(",") for ent in parents.split(";")]])
                    
                curNode = newNode.Node(text,
                                       bool(int(isPredicate)),
                                       feats,
                                       curGraph,
                                       uid = uid)
                
            else:
                for edge,rel in parentsList:
                    digraph.add_edge(curGraph, edge=edge, label=rel)
                ret.append(curGraph)
                flag=True
                
                
    
    fin.close()
    return ret
    

if __name__ == "__main__":
    HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR")+"\\"
    fn  = HOME_DIR+"test_load.prop"
    load_prop_from_file(fn,HOME_DIR)

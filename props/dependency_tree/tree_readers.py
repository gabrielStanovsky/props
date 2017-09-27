import re, fileinput
import logging
from props.graph_representation.graph_wrapper import GraphWrapper, ignore_labels
from props.graph_representation.newNode import Node
from props.graph_representation.word import Word
from props.proposition_structure.syntactic_item import get_verbal_features



pat = re.compile("^(?P<rel>.+)\((?P<head>.+)-(?P<head_id>\d+'*), (?P<dep>.+)-(?P<dep_id>\d+'*)\)$")

import os
from props.dependency_tree.tree import *


def stanford_from_raw(raw_file):
    dir_path = os.path.dirname(os.path.abspath(__file__))+"/stanford_parser/"
    os.chdir(dir_path)
#     convert_command = 'java -cp "*;" edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat "penn" edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz '+ raw_file
    convert_command = 'java -cp "*;" edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat  "penn" -tokenized  -escaper edu.stanford.nlp.process.PTBEscapingProcessor -sentences newline edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz '+ raw_file
    stream = os.popen(convert_command)
    fn = "./tmp.pharsed_based" 
    fout = open(fn,"w")
    for line in stream:
        fout.write(line+"\n")
    fout.close()
    return read_dep_graphs_file(fn,wsjInfo_exists=False,HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR")+"\\")
    
STANFORD_JAR = 'stanford-corenlp-3.3.1.jar'
# Input :   file path of constituency trees
# Output:   stream of the trees converted to dep trees
def convert_to_dep_tree(constituency_tree_fn):
   dir_path = os.path.dirname(os.path.abspath(__file__))
   convert_command = "java -cp {0}/{1} edu.stanford.nlp.trees.EnglishGrammaticalStructure -treeFile {2} -basic -conllx -makeCopulaHead -keepPunct ".format(dir_path, STANFORD_JAR,constituency_tree_fn)
   stream = os.popen(convert_command)
   return stream


def convert_to_dep_graph(constituency_tree_fn):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    convert_command = "java -cp {0}/{1} edu.stanford.nlp.trees.EnglishGrammaticalStructure -treeFile {2} -collapsed -makeCopulaHead -keepPunct -originalDependencies".format(dir_path, STANFORD_JAR,constituency_tree_fn)
    stream = os.popen(convert_command)
    return stream


def convert_json_to_dep_graph(stanford_json_sent):
    """
    Given a Stanford json output,
    return a stream simulating the corresponding to output of convert_to_dep_graph
    """
    with open("tmp.dep", 'w') as fout:
        # Get the basic dependencies and sort by dependent to simulate old format
        # and output this sentence in the older format
        fout.write('\n'.join(["{}({}-{}, {}-{})".format(rel['dep'],
                                                         rel['governorGloss'],
                                                         rel['governor'],
                                                         rel['dependentGloss'],
                                                         rel['dependent'])
                                for rel in sorted(stanford_json_sent['basicDependencies'],
                                                  key = lambda rel: rel['dependent'])]) + "\n\n") # Add new line

    # Return stream (by convention of convert_to_dep_graph
    return open("tmp.dep")


def convert_json_to_dep_tree(stanford_json_sent):
    """
    Given a Stanford json output,
    return a stream simulating the corresponding to output of convert_to_dep_tree (conll format)
    """
    # Align depdencies with tokens
    toks = sorted(stanford_json_sent['tokens'],
                  key = lambda tok: tok['index'])
    basic_dependencies = sorted(stanford_json_sent['basicDependencies'],
                                key = lambda rel: rel['dependent'])

    ret_fn = "tmp.conll"
    with open(ret_fn, 'w') as fout:
        # Get the basic dependencies and sort by dependent to simulate old format
        # and output this sentence in the conll
        fout.write('\n'.join(["\t".join(map(str,
                                            [tok['index'],
                                             tok['originalText'],
                                             '_',
                                             tok['pos'],
                                             tok['pos'],
                                             '_',
                                             rel['governor'],
                                             rel['dep'].lower(),
                                             '_',
                                             '_']))
                              for tok, rel in zip(toks,
                                                  basic_dependencies)]) + '\n\n')

    # Return stream (by convention of convert_to_dep_graph
    return open(ret_fn)


def create_dep_graphs_from_stream(stream,HOME_DIR):
    graphs = []
    init = True
    curGraph = GraphWrapper("",HOME_DIR)
    nodesMap = {}
    for line in stream:
        line = line.strip()
        if line:
            init = False
            m = pat.match(line)
            rel,head,head_id,dep,dep_id = m.groups()
#             head_id = int(head_id)
#             dep_id = int(dep_id)
            if head_id not in nodesMap:
                nodesMap[head_id] = Node(text=[Word(index=int(head_id.split("'")[0]),word=head)],
                                         isPredicate=False,
                                         features={},
                                         gr=curGraph,
                                         orderText=True)
            if dep_id not in nodesMap:
                nodesMap[dep_id] = Node(text=[Word(index=int(dep_id.split("'")[0]),word=dep)],
                                         isPredicate=False,
                                         features={},
                                         gr=curGraph,
                                         orderText=True)
            headNode = nodesMap[head_id]
            depNode = nodesMap[dep_id]
            if curGraph.has_edge((headNode,depNode)): # stanford bug
                curGraph.del_edge((headNode,depNode))
            curGraph.add_edge(edge=(nodesMap[head_id],nodesMap[dep_id]),
                              label =rel)
        if (not line) and (not init):
            init=True
            graphs.append((curGraph,nodesMap))
            curGraph = GraphWrapper("",HOME_DIR)
            nodesMap = {}
    return graphs
                
        
        


# Input :   stream of dep trees converted by Stanford parser
# Output:   List of DepTree
def create_dep_trees_from_stream(stream, wsjInfo_exists, collapsed=False):
    dep_trees = []
    init_flag = True
    wsj_id, sent_id = 0,0
    words = []

    for line in stream:
       line = line.strip()
       # Starting parsing of new tree
       if init_flag:
           if wsjInfo_exists:
               wsj_info = line.split()
               wsj_id, sent_id = wsj_info[0],wsj_info[1]
           else:
               sent_id +=1
           dep_trees_data = {0:[]}
           dep_trees_nodes = {0:DepTree(pos="",word="ROOT",id=0,parent=None,parent_relation="",children=[],wsj_id = int(wsj_id), sent_id = int(sent_id))}
           init_flag = False
           if wsjInfo_exists:
               continue

       # Create DepTree for node in dep tree
       if line != "" :
               node = line.split()
               words.append(node[1])
               id = int(node[0])
               dep_trees_data[id]=node
               dep_trees_nodes[id]=DepTree(pos=node[3],word=node[1],id=node[0],parent=None,parent_relation=node[7],children=[],wsj_id = int(wsj_id), sent_id = int(sent_id))

       # Here all tree nodes are already parsed
       else:
           # Going through all nodes and update connections between them
           for i in filter(lambda x:x,dep_trees_nodes.keys()):
               node_data = dep_trees_data[i]
               node = dep_trees_nodes[i]
               parent_id = int (node_data[6])
               # Set node's parent
               node.set_parent(dep_trees_nodes[parent_id])
               # Set node's parent id
               node.set_parent_id(parent_id)
               # Set the node to the child list of the parent
               dep_trees_nodes[parent_id].add_child(node)
               
           # Add parsed DepTree to the list
           dep_trees_nodes[0].original_sentence = " ".join(words)
           words = []
#            dep_trees.append(copy.copy(dep_trees_nodes))
           yield copy.copy(dep_trees_nodes)
           # Mark for initialization for parsing the next tree
           init_flag = True

#     return dep_trees


def read_trees_file(constituency_tree_fn,
                    wsjInfo_exists=True,
                    stanford_json_sent = None):

   stream = convert_json_to_dep_tree(stanford_json_sent) \
            if stanford_json_sent \
               else convert_to_dep_tree(constituency_tree_fn)

   return create_dep_trees_from_stream(stream,wsjInfo_exists)


def missing_children(treeNode,graphNode):
    neighbors = graphNode.neighbors()
    ret = [Word(index=c.id,word=c.word) for c in treeNode.children if (c.parent_relation not in neighbors) or (c.id != neighbors[c.parent_relation][0].text[0].index) or (c.parent_relation in ignore_labels)]
    return ret

def read_dep_graphs_file(constituency_tree_fn,
                         wsjInfo_exists=False,
                         HOME_DIR="./",
                         stanford_json_sent = None):


    stream = convert_json_to_dep_graph(stanford_json_sent) \
             if stanford_json_sent \
                else convert_to_dep_graph(constituency_tree_fn)

    graphsFromFile = create_dep_graphs_from_stream(stream,HOME_DIR)
    trees = read_trees_file(constituency_tree_fn,
                            False,
                            stanford_json_sent)
    graphs = []
    for i,t in enumerate(trees):
        curGraph,nodesMap = graphsFromFile[i]
        curGraph.originalSentence = t[0].original_sentence
        curGraph.tree_str = "\n".join(t[0].to_original_format().split("\n")[1:])
        curGraph.dep_tree = t
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


def shell():
    import sys
    s = ""
    ts = create_dep_trees_from_stream(sys.stdin, False)
    for t in ts:
        print t
        t[0].draw()
    
#     while True:
#         l = fileinput.input().strip()
#         if not l:
#             if s:
#                 
#         s += fileinput.input()

def readNLTK():
	import sys
	from nltk.tree import Tree
	Tree("".join(map(lambda l: l.strip(), sys.stdin.readlines()))).draw()


if __name__ == "__main__":
	readNLTK()
#    shell()
#     ts = [t[0] for t in create_dep_trees_from_stream(open(r"C:\Users\user\Google_Drive\PHD\AI2 Internship\project\gold_train.txt"), wsjInfo_exists=False)]

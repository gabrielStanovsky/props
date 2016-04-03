# from graph_representation.graph_utils import dumpGraphsToTexFile
import file_handling
import pickle
import copy,time
from nltk import Tree
from location_annotator.textual_location_annotator import textualLocationAnnotator
from applications.apps import extract_properties
from dependency_tree.tree import find_tree_matches
from graph_representation.convert import convert
from graph_representation.graph_wrapper import dumpGraphsToTexFile
from dependency_tree.tree_readers import read_dep_graphs_file
from file_handling import merge
from applications.openIEGS import update_graphs
from constituency_tree.tree_readers import read_trees_file
from graph_representation.annotations.ptb_traces import Traces


HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR")+"\\"
intransitive_verbs = HOME_DIR + "intransitive_verbs.txt"

def qa():
    """
    Runs graph parsing for all trees in ptb.
    returns a list of trees which caused exceptions
    """
    start = time.time() 
    
    problematic=[]

    # load dep trees from file
    graphsInput=merge(treesFile=HOME_DIR+"ptb.dp", graphFile=HOME_DIR+"ptb_collapsed.dp")
    
    
                      
    for i,tree in enumerate(graphsInput):
        print ",".join([str(i)])#,str(tree.wsj_id),str(tree.sent_id)])
        tree_copy = copy.deepcopy(tree)
        try:
            g = convert(tree)
        except Exception as e:
            print str(i)+"PROBLEM"
            problematic.append((i,tree_copy))
    f = open(HOME_DIR+"problematic.p",'w')
    pickle.dump(problematic, f)
    f.close()
    end=time.time()
    
    print "parsing time {0}".format(end-start)
    
    if len(problematic)==0:
        print "ALL GOOD"
    else:
        print "PROBLEMS!"

    return problematic,graphsInput

def handle_problematic():
    """
    try to parse all problematic trees from the pickle file.
    """
    f = open(HOME_DIR+"problematic.p")
    problematic = pickle.load(f)
    f.close()
          
    graphs = []
          
    for i,tree in problematic:
        print i
        curGraph = convert(tree)
        graphs.append(curGraph)
    return graphs


def barrons(tla):
    start = time.time()
    # load dep trees from file
#     trees=file_handling.load_depTrees_from_file(HOME_DIR+"PTB_hundreds.dp")
    trees=file_handling.load_depTrees_from_file(HOME_DIR+"barrons-processed-tokenized.dp",wsjInfo_exists=False)
    sorted_trees = sorted(trees,key=lambda t: len(t.get_original_sentence().split()),reverse=True)
    fout = open(HOME_DIR+"barrons_100_dep.txt",'w')
    appendix={}
    for key in parse_graph.APPENDIX_KEYS:
        appendix[key] = []
    graphs = []
         
    graphCounter = 0
    for i,tree in enumerate(trees):
        
        fout.write(tree.to_original_format()+"\n")
        print ",".join([str(tree.wsj_id),str(tree.sent_id)])
        curGraph = GraphRepresentation(tree,tla)
             
        if curGraph.gTag:
            graphs.append(curGraph)
            for key in curGraph.types.getSet():
                if key not in appendix: #TODO: this should not happen
                    appendix[key]=[]
                appendix[key].append(graphCounter)
            graphCounter+=1
    fout.close()
    end=time.time()
    
    print "parsing time {0}".format(end-start)
         
    #dumpGraphsToTexFile(graphs= graphs,graphsPerFile = 1500,appendix = appendix,lib=HOME_DIR+"/pdf/")
    return graphs


def counterAll(graph):
    return graph.types.getSet()
    

def main(fileType,counterFunction=counterAll,counterLimit=50000):
    
    # load dep trees from file
#     trees=file_handling.load_depGraphs_from_file(HOME_DIR+"PTB_collapsed_hundreds.dp",wsjInfo_exists=False)
#     sorted_trees = sorted(trees,key=lambda t: len(t.get_original_sentence().split()),reverse=True)
    
    graphsInput=merge(treesFile=HOME_DIR+"ptb_hundreds.dp", graphFile=HOME_DIR+"ptb_collapsed_hundreds.dp")
#     graphsInput=merge(treesFile=HOME_DIR+"ptb_h.dp", graphFile=HOME_DIR+"ptb_collapsed.dp")
    tree_gen = read_trees_file(open(HOME_DIR+"TB"))
    ptb_trees = [tree_gen.next() for _ in graphsInput]
    counter = 0
    traces = Traces()
    appendix={}
#     for key in parse_graph.APPENDIX_KEYS:
#         appendix[key] = []
    graphs = []
    start = time.time()
    for i,graph in enumerate(graphsInput):
        print ",".join([str(i)])
        if i == 80:
            print "1"
        curGraph = convert(graph)
        curPtb = ptb_trees[i]
        traces.annotate(gr=curGraph, phrase_based_tree=curPtb, t=curGraph)
        
        curTypes =counterFunction(graph) 
        if curTypes:
            graphs.append(curGraph)
            for key in curTypes:
                curEntry = appendix.get(key,[])
                curEntry.append(counter)
                appendix[key] = curEntry
    
            counter+=1
            if counter >= counterLimit:
                break
        
             
    end=time.time()
    
    print "parsing time {0}".format(end-start)
    print "found {0} matches".format(counter)
   
    dumpGraphsToTexFile(graphs= graphs,graphsPerFile = 1500,appendix = appendix,lib=HOME_DIR+"/pdf/",outputType=fileType)

    return graphs

def apply_match():
    trees=file_handling.load_depTrees_from_file(HOME_DIR+"PTB.dp")
    
        
    pat = Tree("(self._VERBAL_PREDICATE_FEATURE_Lemma() =='have')",
               [Tree("(self.parent_relation in subject_dependencies)",[]),
                Tree("(self.parent_relation in object_dependencies)",[])])
#                [Tree("(self.parent_relation=='ccomp') or (self.parent_relation=='xcomp')",[]),
#                 Tree("(self.parent_relation=='obj') or (self.parent_relation=='dobj') or (self.parent_relation=='iobj')",[]),
#                 Tree("(self.parent_relation=='obj') or (self.parent_relation=='dobj') or (self.parent_relation=='iobj')",[])])
#                 #Tree("$+(self.parent_relation=='ccomp')",
                 
    ls1 = []
    for t in trees:
        ls1.extend(find_tree_matches(tree =t[0] , pat = pat))
    return ls1
        
#     pat = Tree("(self.is_verbal_predicate())",[])
#                [Tree("(self.parent_relation in object_dependencies)",[])])
#                [Tree("(self.parent_relation=='ccomp') or (self.parent_relation=='xcomp')",[]),
# #                 Tree("(self.parent_relation=='obj') or (self.parent_relation=='dobj') or (self.parent_relation=='iobj')",[]),
# #                 Tree("(self.parent_relation=='obj') or (self.parent_relation=='dobj') or (self.parent_relation=='iobj')",[])])
# #                 #Tree("$+(self.parent_relation=='ccomp')",
#                  
#     ls2 = []
#     for t in trees:
#         ls2.extend(find_tree_matches(tree =t[0] , pat = pat))
#     return ls1,ls2


def counterFunction(graph):
    curTypes = list(graph.types.getSet())
    return [x for x in curTypes if "conditionals-because" in x]

def tests():
        const_t = ["""( (S 
    (NP-SBJ (NNP Mr.) (NNP Vinken) )
    (VP (VBZ is) 
      (NP-PRD 
        (NP (NN chairman) )
        (PP (IN of) 
          (NP 
            (NP (NNP Elsevier) (NNP N.V.) )
            (, ,) 
            (NP (DT the) (NNP Dutch) (VBG publishing) (NN group) )))))
    (. .) ))
"""] 
        gs = update_graphs(const_trees=const_t, goldStandard=True)
        g = gs[0]
        s = g.to_latex()
        print s

if __name__ == "__main__":
    
#     locationFilename = HOME_DIR+"locations/empty.txt"
#     lexicon = HOME_DIR+"locations/lexicon.txt"
#     tla = textualLocationAnnotator(locationFilename,
#                                    lexicon)
#     import pickle
#     fin = open(HOME_DIR+"acomp.p")
#     trees= pickle.load(fin)
#     fin.close()
#     graphs=[]
#     for t in trees[:100]:
#         curGraph = GraphRepresentation(t,tla)
#         graphs.append(curGraph)
#              
#     dumpGraphsToTexFile(graphs= graphs,graphsPerFile = 1500,appendix = {},lib=HOME_DIR+"/pdf/",outputType='html')
         
#     gs = barrons(tla)
#     for g in gs:
#         extract_properties(g.gr,HOME_DIR+"extractions.txt")
#     problematic,trees = qa()
#     gs = handle_problematic()


    gs= main("html",counterAll,counterLimit=250)


#     g = convert(gs[0])
#     ls1 = apply_match()
#
# 
#     
#     


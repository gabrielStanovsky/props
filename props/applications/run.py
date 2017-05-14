from props.dependency_tree.tree_readers import read_trees_file, read_dep_graphs_file
from props.applications.viz_tree import DepTreeVisualizer
from subprocess import call
from props.graph_representation.graph_wrapper import GraphWrapper
from props.proposition_structure.syntactic_item import get_verbal_features
from copy import copy
from props.graph_representation.convert import convert
from StringIO import StringIO
import logging


import os,sys
from BerkeleyInterface import *
global parser,opts


BASE_PATH = os.path.join(os.path.dirname(__file__), '../')

def load_berkeley(tokenize=True,
                  path_to_berkeley = os.path.join(BASE_PATH, 'berkeleyparser/')):
    # This should be the path to the Berkeley Parser jar file
    cp = os.path.join(path_to_berkeley, "BerkeleyParser-1.7.jar")
    logging.info("Starting Berkeley parser from {0}".format(cp))
    startup(cp)
    
    gr = os.path.join(path_to_berkeley, 'eng_sm6.gr')
    args = {"gr":gr, "tokenize":tokenize}
    
    # Convert args from a dict to the appropriate Java class
    global opts
    opts = getOpts(dictToArgs(args))
    
    # Load the grammar file and initialize the parser with our options
    global parser
    parser = loadGrammar(opts)


def parseSentences(sent, HOME_DIR = BASE_PATH):
    orig_Stdin = sys.stdin
    strIn = StringIO(sent)
    sys.stdin = strIn
    strOut = StringIO()
    parseInput(parser, opts, outputFile=strOut)
    sys.stdin = orig_Stdin
    # Now we can retrieve the output as a string:
    result = strOut.getvalue()
#     print result
    tmp_fn = "./tmp.tmp"
    fout = open(tmp_fn,'w')
    fout.write(result)
    fout.close()
    graphs = read_dep_graphs_file(tmp_fn,False,HOME_DIR)
    ret = []
    for graph in graphs:        
        g = convert(graph)
        ret.append((g,g.tree_str))

    if not graphs:#Berkley bug?
        ret.append((GraphWrapper("",HOME_DIR),""))

    strIn.close()
    strOut.close()
    return ret

if __name__ == "__main__":
    HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR", ".")

    fail = HOME_DIR+"fail.svg"
    load_berkeley()
    try:
        while True:
            gs = parseSentences(raw_input("> "),HOME_DIR)
            for g,tree in gs:
                if tree:
                    g.draw()
                else:
                    call('"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" '+fail)
    finally:
        shutdown()
        
HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR", ".")

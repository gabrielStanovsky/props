import file_handling

from graph_representation.graph_wrapper import  dumpGraphsToTexFile
from graph_representation.annotations.manual_annotations import ManualAnnotation
from graph_representation import parse_graph
from graph_representation.convert import convert
import time




if __name__ == "__main__":

    JESSICA,GABI=(0,1)
    USERS = {JESSICA: "C:\\Users\\user\\PycharmProjects\\propextraction\\",
                 GABI: "C:\\Users\\user\\git\\propextraction\\"}
    USER = JESSICA
    HOME_DIR = USERS[USER]

    # load dep trees from file
    trees=file_handling.load_depTrees_from_file(HOME_DIR+"PTB.dp")[0:101]
    manual_annotation = ManualAnnotation(vadas=False,nombank=False,traces=True,light_verbs=False,relative_path=HOME_DIR)
    from location_annotator.textual_location_annotator import textualLocationAnnotator
    locationFilename = HOME_DIR+"locations/locations_processed.txt"
    lexicon = HOME_DIR+"locations/lexicon.txt"
    tla = textualLocationAnnotator(locationFilename,lexicon)
    appendix={}
    for key in parse_graph.APPENDIX_KEYS:
        appendix[key] = []
    graphs = []
    start = time.time()
    graphCounter = 0
    for i,tree in enumerate(trees):

        curGraph = convert(tree)
        manual_annotation.annotate(tree,curGraph)
        if curGraph.gTag:
            graphs.append(curGraph)
            for key in curGraph.types.getSet():
                if key not in appendix: #TODO: this should not happen
                    appendix[key]=[]
                appendix[key].append(graphCounter)
            graphCounter+=1
    end=time.time()

    print "parsing time {0}".format(end-start)

    dumpGraphsToTexFile(graphs= graphs,graphsPerFile = 1500,appendix = appendix,lib=HOME_DIR+"/pdf/",outputType='pdf')
    # if manual_annotation.to_pdf_counter:
    #    dumpGraphsToTexFile(graphs= manual_annotation.to_pdf_graphs,graphsPerFile = manual_annotation.to_pdf_counter,appendix = manual_annotation.to_pdf_appendix,lib=HOME_DIR+"pdf\\",outputType='pdf')



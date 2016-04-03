import file_handling
from graph_representation.to_graph_representation import GraphRepresentation
from graph_representation.graph_utils import dumpGraphsToTexFile
from graph_representation.annotations.manual_annotations import ManualAnnotation
from graph_representation import parse_graph
from graph_representation.node import ConjunctionNode,CopularNode
import time

class Heuristics:

    def annotate(self,gr):
        sub = self.subject_of_conj_components(gr)
        obj = self.object_of_conj_components(gr)
        syntactic_variations = self.eliminate_syntactic_variations(gr)
        return sub or obj or syntactic_variations

    def subject_of_conj_components(self,gr):
        flag = False
        for node in gr.gr.nodes():
            if not isinstance(node,ConjunctionNode):
                continue
            not_predicate_childs = [ch for ch in gr.gr.neighbors(node) if (not ch.isPredicate) or isinstance(ch,CopularNode)]
            if not_predicate_childs:
                continue

            # find conjunction components with a subj and with no subj
            ch_subj = {}
            ch_no_subj = []
            for ch in gr.gr.neighbors(node):
                for chch in gr.gr.neighbors(ch):
                    if gr.gr.edge_label((ch,chch)).find("sbj") > -1 or gr.gr.edge_label((ch,chch)).find("sub") > -1:
                        ch_subj[ch] = chch
                if ch not in ch_subj.keys():
                    ch_no_subj.append(ch)

            # if there is only one subject, connect is as a subject of the rest
            if len(set(ch_subj.values())) == 1 and ch_no_subj:
                subj = ch_subj.values()[0]
                for ch in ch_no_subj:
                    if not gr.gr.is_edge_exists(ch,subj) and min([x.index for x in subj.text]) < min([x.index for x in ch.text]):
                        flag = True
                        gr.types.add("Heuristics - Subject")
                        ch_subj.values()[0].features["heuristics"] = True
                        gr.gr.add_edge((ch,subj),"h-sub")
        return flag

    def object_of_conj_components(self,gr):
        flag = False
        for node in gr.gr.nodes():
            if not isinstance(node,ConjunctionNode):
                continue
            not_predicate_childs = [ch for ch in gr.gr.neighbors(node) if (not ch.isPredicate) or isinstance(ch,CopularNode)]
            if not_predicate_childs:
                continue

            ch_obj = {}
            ch_no_obj = []
            for ch in gr.gr.neighbors(node):
                for chch in gr.gr.neighbors(ch):
                    if gr.gr.edge_label((ch,chch)).find("obj") > -1 :
                        ch_obj[ch] = chch
                if ch not in ch_obj.keys():
                    ch_no_obj.append(ch)

            if len(set(ch_obj.values())) == 1 and ch_no_obj:
                obj = ch_obj.values()[0]
                max_key_ind = max([x.index for key,_ in ch_obj.iteritems() for x in key.text] )
                for ch in ch_no_obj:
                    min_ch_ind = min([x.index for x in ch.text])
                    # the object should be after the predicate and related to a predicate that is before the current predicate
                    if not gr.gr.is_edge_exists(ch,obj) and min([x.index for x in obj.text]) > min_ch_ind and min_ch_ind > max_key_ind:
                        flag = True
                        gr.types.add("Heuristics - Object")
                        ch_obj.values()[0].features["heuristics"] = True
                        gr.gr.add_edge((ch,obj),"h-obj")
        return flag


    def eliminate_syntactic_variations(self,gr):
        flag = False
        # going to
        for node in gr.gr.nodes():
            if node.isPredicate and len(node.str)==1 and "go" == node.str[0].word :
                v = None
                for child in gr.gr.neighbors(node):
                    if child.isPredicate:
                        v = child
                        break
                for child in gr.gr.neighbors(node):
                    if child == v:
                        continue
                    label = gr.gr.edge_label((node,child))
                    gr.gr.add_edge((v,child),label)
                gr.gr.del_node(node)
                flag = True
        return flag


if __name__ == "__main__":

    JESSICA,GABI=(0,1)
    USERS = {JESSICA: "C:\\Users\\user\\PycharmProjects\\propextraction\\",
                 GABI: "C:\\Users\\user\\git\\propextraction\\"}
    USER = JESSICA
    HOME_DIR = USERS[USER]

    # load dep trees from file
    trees=file_handling.load_depTrees_from_file(HOME_DIR+"PTB_few.dp")
    manual_annotation = ManualAnnotation(vadas=False,nombank=False,traces=False,light_verbs=False,relative_path=HOME_DIR)
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
    heuristics = Heuristics()
    for i,tree in enumerate(trees):

        curGraph = GraphRepresentation(tree,tla)
        manual_annotation.annotate(tree,curGraph)
        if curGraph.gTag and heuristics.annotate(curGraph):
            graphs.append(curGraph)
            for key in curGraph.types.getSet():
                if key not in appendix: #TODO: this should not happen
                    appendix[key]=[]
                appendix[key].append(graphCounter)
            graphCounter+=1
    end=time.time()

    print "parsing time {0}".format(end-start)

    dumpGraphsToTexFile(graphs= graphs,graphsPerFile = 1500,appendix = appendix,lib=HOME_DIR+"pdf\\",outputType='html')


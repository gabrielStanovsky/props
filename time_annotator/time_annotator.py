#from py4j.java_gateway import JavaGateway
import json
from collections import defaultdict
from annotation import Annotation

class TimeAnnotator:

    def __init__(self, file_name):
        self.file_name = file_name
        self.annotations = []
        self._load_annotations()

    def _load_annotations(self):
        f = open(self.file_name,'r')
        for line in f:
            line = line.strip()
            if line != "":
                annotations_list = [Annotation(int(begin_index) + 1, int(end_index), time_expression, timex3) for begin_index, end_index, time_expression, timex3 in map(None, *([iter(line.split("\t"))] * 4))]
            else:
                annotations_list = []

            self.annotations.append(annotations_list)
        f.close()




    # wrapper for java API
    """def __init__(self):
        self.gateway = JavaGateway()
        self.annotator = self.gateway.entry_point


    def annotate(self,text):
        annotation_result_json = self.annotator.annotate(text)
        if annotation_result_json:
            annotation_result = json.loads(annotation_result_json)

            return (True,annotation_result["time_exp"], (annotation_result["token_begin"],annotation_result["token_end"]))
        return (False,0,0)"""

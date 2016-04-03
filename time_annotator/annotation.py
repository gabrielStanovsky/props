
from xml.dom import minidom
from dateutil import parser
class Annotation:

    def __init__(self, begin_token_index, end_token_index, time_expression, timex3):
        self.begin_token_index = begin_token_index
        self.end_token_index = end_token_index
        self.time_expression = time_expression
        self.ref = None
        self.value = None
        self.parsed_value = None
        self.type = None
        self.timex3 = timex3

        self.parse_timex3()


    def parse_timex3(self):
        # parse annotation type and value
        parsed_xml = minidom.parseString(self.timex3).getElementsByTagName("TIMEX3")[0]
        if parsed_xml.hasAttribute("type"):
            self.type = parsed_xml.attributes["type"].value
        if parsed_xml.hasAttribute("value"):
            self.value = parsed_xml.attributes["value"].value
            # check if the value is REF, if not parse the value as ISO8601
            if self.value.find("_REF")>-1 :
                self.ref = self.value.split("_")[0]
            else:
                self.parse_timex3_value_iso8601()

    def parse_timex3_value_iso8601(self):
        if self.type == "TIME" or self.type == "DATE":
                try:
                    self.parsed_value = parser.parse(self.value)
                except:
                    None
                    #print repr(self.value)




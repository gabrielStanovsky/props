"""
Usage:
  parse_props.py [FILE] (-g|-t) [--original] [--oie] [--dep] [--tokenized] [--dontfilter|--corenlp-json-input]
  parse_props.py (-h|--help)

Parse sentences into the PropS representation scheme

Arguments:
  FILE   input file composed of one sentence per line. if not specified, will use stdin instead

Options:
  -h                      Display this help
  -t                      Print textual PropS representation
  -g                      Print graphical representation (in svg format)
  --original              Print original sentence
  --oie                   Pint open-ie like extractions
  --dep                   Print the intermediate dependency representation 
  --tokenized             Specifies that the input file is tokenized
  --dontfilter            Skip pre-filtering the input file to only printable characters
  --corenlp-json-input    Take Stanford's output json as input (either from STDIN or from file).
"""

#!/usr/bin/env python
#coding:utf8

import os, sys, string
HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR", './')+"/"

import run
import json
from props.webinterface import bottle
from props.applications.viz_tree import DepTreeVisualizer
from props.applications.run import load_berkeley
import fileinput
bottle.debug(True)
import os.path
import codecs
from cStringIO import StringIO
import sys,time,datetime
from subprocess import call
from docopt import docopt
from props.applications.run import parseSentences
import logging

def main(arguments):
    if not(arguments["--corenlp-json-input"]):
        #Initialize Berekeley parser when using raw input 
        load_berkeley(not arguments["--tokenized"])

    outputType = 'html'
    sep = "<br>"
    if arguments['-t']:
        outputType = 'pdf'
        sep = "\n"
        
    graphical = (outputType=='html')

    # Parse according to source input
    if arguments["--corenlp-json-input"]:
        # Parse accroding to input method
        sents = (json.loads("".join(arguments["FILE"])) \
                 if isinstance(arguments["FILE"], list) \
                 else json.load(arguments["FILE"]))["sentences"]

    elif arguments["--dontfilter"]:
        sents = [x for x in arguments["FILE"]]
    else:
        sents = [filter(lambda x: x in string.printable, s) for s in arguments["FILE"]] 

    
    for sent in sents:
        gs = parseSentences(sent,
                            HOME_DIR,
                            stanford_json_sent = arguments["--corenlp-json-input"])
        g,tree = gs[0]
        dot = g.drawToFile("","svg")   
        
        # deptree to svg file
        d = DepTreeVisualizer.from_conll_str(tree)
        
        # print sentence (only if in graphical mode)
        if (arguments["--original"]):
            print(sent+sep)
            
        #print dependency tree
        if (arguments['--dep']):
            if graphical:
                print(d.as_svg(compact=True,flat=True)+sep)
            else:
                print(tree)
        
        #print PropS output
        if graphical:        
            print(dot.create(format='svg')+sep)
        else:
            print(g)
        
        #print open ie like extractions
        if (arguments["--oie"]):
            print(sep.join([str(prop) for prop in g.getPropositions(outputType)]))
            
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    arguments = docopt(__doc__)
    logging.debug(arguments)
    if arguments["FILE"]:
        arguments["FILE"] = open(arguments["FILE"])
    else:
        arguments["FILE"] = [s for s in sys.stdin]

    main(arguments)



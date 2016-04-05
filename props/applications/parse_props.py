"""
Usage:
  parse_props.py [FILE] (-g|-t) [--original] [--oie] [--dep] [--tokenized] [--dontfilter]
  parse_props.py (-h|--help)

Parse sentences into the PropS representation scheme

Arguments:
  FILE   input file composed of one sentence per line. if not specified, will use stdin instead
  
Options:
  -h             display this help
  -t             print textual PropS representation
  -g             print graphical representation (in svg format)
  --original     print original sentence
  --oie          print open-ie like extractions
  --dep          print the intermediate dependency representation 
  --tokenized    specifies that the input file is tokenized
  --dontfilter   skip pre-filtering the input file to only printable characters
"""

#!/usr/bin/env python
#coding:utf8

import os, sys, string
HOME_DIR = os.environ.get("PROPEXTRACTION_HOME_DIR", './')+"/"

import run  
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
import svg_stack as ss
from docopt import docopt
from props.applications.run import parseSentences


def main(arguments):
    
    load_berkeley(not arguments["--tokenized"])
    
    outputType = 'html'
    sep = "<br>"
    if arguments['-t']:
        outputType = 'pdf'
        sep = "\n"
        
    graphical = (outputType=='html')
    
    if arguments["--dontfilter"]:
        sents = [x for x in arguments["FILE"]]
    else:    
        sents = [filter(lambda x: x in string.printable, s) for s in arguments["FILE"]] 
        
    for sent in sents:
        
        gs = parseSentences(sent,HOME_DIR)
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
    arguments = docopt(__doc__)
    if arguments["FILE"]:
        arguments["FILE"] = open(arguments["FILE"])
    else:
        arguments["FILE"] = sys.stdin
    main(arguments)



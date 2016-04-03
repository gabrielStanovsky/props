#!/usr/bin/env python
#coding:utf8
from webinterface.bottle import route, run, get, post, request, response, static_file
from webinterface.log import log
import applications.run  
from webinterface import bottle
from applications.viz_tree import DepTreeVisualizer
from applications.run import load_berkeley
bottle.debug(True)
import os.path
import codecs
from cStringIO import StringIO
import sys,time,datetime
from subprocess import call
import svg_stack as ss


try:
   PORT=int(sys.argv[1])
except:
   PORT=8081

@get('/gparse')
def gparse():
    print "in gparse"
    sent = request.GET.get('text','').strip()
#    sent = request.forms.get("text").decode("utf8")
    print sent
    sents = sent.strip().replace(". ",".\n").replace("? ","?\n").replace("! ","!\n").split("\n")
    sent = sents[0]
    gs = applications.run.parseSentences(sent,"./")
    g,tree = gs[0]
    if tree:
        # graph to svg file
        ts = time.time()
        filename = "./parses/"+datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H:%M:%S')
        g.drawToFile(filename+"_g","svg")
        
        # deptree to svg file
        d = DepTreeVisualizer.from_conll_str(tree)
        fout = open(filename+"_t.svg",'w')
        fout.write(d.as_svg(compact=True,flat=True))
        fout.close()
        
        
        #merge
        doc = ss.Document()
        layout1 = ss.VBoxLayout()
        layout1.addSVG(filename+"_t.svg",alignment=ss.AlignTop|ss.AlignHCenter)
        layout1.addSVG(filename+"_g.svg",alignment=ss.AlignCenter)
        doc.setLayout(layout1)
        doc.save(filename+'.svg')
        
        
        ret = "<html>EXPERIMENTAL VERSION<br><a href =./gparse?{0}>link</a><br><br>{1}<br><br>".format(request.query_string,file(filename+".svg").read())
        ret += '<font size="5">'
        ret += '<br>'.join([str(prop) for prop in g.getPropositions('html')])
        ret += "</html>"
    else:
        ret = "<html>Something went wrong<br><br>{0}".format(file("./fail.svg").read())
    
    
    return ret
#     return codecs.open(os.path.join(HERE,'mytree.htm'),encoding="utf8").read().replace('__BLA__', deptreedraw.tree_js(_sent)).replace('__SENT__',sent);

load_berkeley()
run(host='',port=PORT)


# doc = ss.Document()
# layout1 = ss.VBoxLayout()
# layout1.addSVG(HOME_DIR+"dtvis.svg",alignment=ss.AlignTop|ss.AlignHCenter)
# layout1.addSVG(HOME_DIR+"merged.svg",alignment=ss.AlignCenter)
# doc.setLayout(layout1)
# doc.save(HOME_DIR+'qt_api_test.svg')

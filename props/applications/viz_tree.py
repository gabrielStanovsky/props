from xml.etree import ElementTree as et
import cStringIO as strio
from collections import defaultdict

square_edges = True

class DepTreeNode:
    def __init__(self, form, node_id, tag=None):
        self.form = form
        self.tag = tag
        self.nid = node_id

    def length(self):
        if self.tag: return max(len(self.form),len(self.tag))
        else: return len(self.form)

class DepTreeArc:
    def __init__(self, head_node_id, mod_node_id, label=None):
        self.head_node_id = head_node_id
        self.mod_node_id = mod_node_id
        self.label = label

    def length(self): return abs(int(self.head_node_id) - int(self.mod_node_id))

class NodeViz:
    fontsize = 16
    word_spacing = 16
    letter_width = 10
    def __init__(self, node, x, y, rotate=0):
        self.nodeinfo = node
        self.x = x
        self.y = y
        #self.width = node.length() * self.letter_width 
        self.width = len(node.form) * self.letter_width
        if node.tag:
            self.width += (len("/" + str(node.tag)) * self.letter_width)
        self.height = self.fontsize
        self.rotate = ""
        if rotate:
            self.width = self.fontsize
            self.rotate = "rotate(%s %s,%s)" % (rotate,self.x,self.y)
            # could add some trig to make it more accurate, but no real need.
            self.height = node.length() * self.letter_width 

    def center_x(self): return self.x + (self.width / 2)
    def top(self): return self.y - self.fontsize
    def bottom(self): return self.y

    def svg(self,ctx):
        n = et.SubElement(ctx, 'text', 
                {  'font-family':'monospace',
                    'font-size':'%s' % self.fontsize}, 
                x=str(self.x),
                y=str(self.y), transform=self.rotate)
        n.text = self.nodeinfo.form
        if self.nodeinfo.tag: n.text += "/" + str(self.nodeinfo.tag)
        #et.SubElement(ctx,'rect',x=str(self.x),y=str(self.y),width=str(self.width),height='16')

def point_on_bazier(f,x0,y0,x1,y1,x2,y2,x3,y3):
    x = (x0*((1-f)**3)) + (x1*3*((1-f)**2)*f) + (x2*3*(1-f)*f*f) + (x3*f**3)
    y = (y0*((1-f)**3)) + (y1*3*((1-f)**2)*f) + (y2*3*(1-f)*f*f) + (y3*f**3)
    return x,y

class ArcViz:
    def __init__(self, arc, nodes_map, d=0):
        self.nodes_map = nodes_map
        self.arc = arc
        if nodes_map:
            self.head_node = nodes_map[arc.head_node_id]
            self.mod_node = nodes_map[arc.mod_node_id]
        self.label = arc.label
        self.d = d + 1

    def color(self):
        return "blue"

    def height(self):
        assert(square_edges)
        control = self.d * 20
        return control / 1.5 + 10 #10 is label font size.

    def svg(self,ctx):
        h = self.head_node.center_x()
        m = self.mod_node.center_x()
        if h > m:
            xm = m 
            xh = h - 5  
            x = -10
            marker = "marker-end"
        else:
            xh = h + 5 
            xm = m 
            x = 10
            marker = "marker-end"

        pathid = str(hash(self)).replace("-","A")
        yh = self.head_node.top()
        ym = self.mod_node.top()
        if (yh == ym):
            #control = abs(xh - xm) / 2 + 3
            if self.d: control = self.d * 20

            path = " ".join(map(str,["M",xh,yh,"C",xh + x , yh - control, xm - x , ym - control, xm, ym]))
            midx,midy = point_on_bazier(0.5,xh,yh,xh+x,yh-control,xm-x,ym-control,xm,ym)

            if square_edges:
                path = " ".join(map(str,["M",xh,yh,"L",xh + x , yh - (control / 1.5), "L", xm - x , ym - (control / 1.5), "L", xm, ym]))
                midx,midy = (xm - xh) / 2 + xh, yh - (control / 1.5)
            #arrow = " ".join(map(str,["M", m - 3, ys - 3, "L", m, ys, "L", m + 3, ys -3]))
            lblx = midx
            lbly = midy - 2
            lblanc = "start" if h < m else "end"
        else:
            yh = self.head_node.bottom()
            ym = self.mod_node.top() - 10
            path = " ".join(map(str,["M",xh,yh,"L", xm, ym]))
            lblx = xm
            lbly = self.mod_node.top()
            lblanc = "middle"

        arc = et.SubElement(ctx, "path", {"stroke-width":"2px", marker: 'url(#marker)'}, d=path, fill='none', stroke=self.color(),id=pathid)
        lbl = et.SubElement(ctx, "text", {"font-size":"10","text-anchor":lblanc,"font-family":"sans-serif"}, y=str(lbly), x=str(lblx),fill="red")
        lbl.text = self.label

        et.SubElement(lbl, 'set', attributeName="font-weight", to="bold", begin="%s.mousemove" % pathid, end="%s.mouseout" % pathid)
        et.SubElement(arc, 'set', attributeName="stroke-width", to="4px", begin="%s.mousemove" % pathid, end="%s.mouseout" % pathid)
        #et.SubElement(ctx, "path", d=arrow, fill='none', stroke='black')

class ArcVizDirColor(ArcViz):
    def color(self):
        if self.head_node.center_x() > self.mod_node.center_x(): return "green"
        return "blue"

class DepTreeVisualizer:
    def __init__(self):
        self.nodes = []
        self.nodes_by_id = {}
        self.arcs = []
        self.node_depths = {}

    def add_node(self, node):
        self.nodes_by_id[node.nid] = node
        self.nodes.append(node)

    def add_arc(self, arc):
        assert(arc.head_node_id in self.nodes_by_id),arc.head_node_id
        assert(arc.mod_node_id in self.nodes_by_id),arc.mod_node_id
        self.arcs.append(arc)
        #a = int(arc.head_node_id),int(arc.mod_node_id)
        #l = min(a)
        #r = max(a)
        #self.arcs_by_left[l] = (r,arc)

    def calc_node_depths(self):
        depths = {}
        def annotate(node, mods, d):
            depths[node] = d
            for m in mods[node]: annotate(m,mods,d+1)
        mods = defaultdict(list)
        for arc in self.arcs:
            h,m = arc.head_node_id,arc.mod_node_id
            mods[h].append(m)
        annotate(0,mods, 0)
        return depths

    def flat_layout_as_svg(self, compact=True): #{{{
        node_depths = self.calc_node_depths()
        
        #ArcViz = ArcVizDirColor
        # sorted list of arc lengths, to calculate the rank-length of each arc
        alens = list(sorted(set([a.length() for a in self.arcs])))
        max_arc_height = max([ArcViz(a, None, alens.index(a.length())).height() for a in self.arcs])
        
        words_y = max_arc_height + NodeViz.fontsize

        x = 0
        viz_nodes = {}
        last_node_in_depth = {}
        max_word_height = 0
        for node in self.nodes:
            rotate=45 if compact else 0
            n = NodeViz(node, x, words_y, rotate=rotate)
            x += n.width + NodeViz.word_spacing
            max_word_height = max(max_word_height, n.height)
            viz_nodes[node.nid] = n
        max_x = x
        if rotate: max_x += 40 # if the last word is long.. TODO make nicer
        max_y = words_y + max_word_height

        doc = et.Element('svg', xmlns='http://www.w3.org/2000/svg', version="1.1")
        marker = et.XML("""<defs><marker id="marker" viewBox="0 0 10 10" refX="7" refY="5" markerUnits="strokeWidth" orient="auto" markerWidth="4" markerHeight="5"> <polyline points="0,0 10,5 0,10 1,5" stroke="currentColor" /> </marker></defs>""")
        doc.append(marker)

        #et.SubElement(doc,'line',x1="0",x2="100",y1=str(max_y),y2=str(max_y),stroke="black")

        for n in viz_nodes.values():
            n.svg(doc)

        for arc in self.arcs:
            a = ArcViz(arc, viz_nodes, d=alens.index(arc.length()))
            a.svg(doc)

        doc.attrib["width"] = str(max_x)
        doc.attrib["height"] = str(max_y)
        
        return doc
    #}}}

    def tree_layout_as_svg(self, compact=True): #{{{
        node_depths = self.calc_node_depths()
        x = 0
        viz_nodes = {}
        last_node_in_depth = {}
        for node in self.nodes:
            n = NodeViz(node, x, NodeViz.fontsize + (node_depths[node.nid] * 50), rotate=0)
            #TODO: smarter layout for "compact"
            x += n.width + NodeViz.word_spacing
            max_y = NodeViz.fontsize + 5 + (max(node_depths.values())*50)
            viz_nodes[node.nid] = n
        max_x = x

        doc = et.Element('svg', xmlns='http://www.w3.org/2000/svg', version="1.1")
        marker = et.XML("""<defs><marker id="marker" viewBox="0 0 10 10" refX="7" refY="5" markerUnits="strokeWidth" orient="auto" markerWidth="4" markerHeight="5"> <polyline points="0,0 10,5 0,10 1,5" stroke="currentColor" /> </marker></defs>""")
        doc.append(marker)

        for n in viz_nodes.values():
            n.svg(doc)

        #ArcViz = ArcVizDirColor
        for arc in self.arcs:
            a = ArcViz(arc, viz_nodes, d=0)
            a.svg(doc)

        doc.attrib["width"] = str(max_x)
        doc.attrib["height"] = str(max_y)
        
        return doc
    #}}}

    def _repr_svg_(self):
        return self.as_svg(True, True)

    def as_svg(self, compact=True, flat=False, as_obj=False):
        if flat: doc = self.flat_layout_as_svg(compact)
        else: doc = self.tree_layout_as_svg(compact)

        if as_obj: return doc
        else:return et.tostring(doc)

    def as_svg_old(self,compact=True,flat=False,as_obj=False): #{{{
        node_depths = self.calc_node_depths()
        x = 0
        viz_nodes = {}
        last_node_in_depth = {}
        max_word_height = 0
        for node in self.nodes:
            if flat:
                y = 150
                rotate=45 if compact else 0
                n = NodeViz(node, x, y, rotate=rotate)
                x += n.width + NodeViz.word_spacing
                max_word_height = max(max_word_height, n.height)
                max_y = 360
            else:
                n = NodeViz(node, x, 10 + (node_depths[node.nid] * 50), rotate=0)
                #TODO: smarter layout for "compact"
                x += n.width + NodeViz.word_spacing
                max_y = 10 + (max(node_depths.values())*50)
            viz_nodes[node.nid] = n
        max_x = x

        doc = et.Element('svg', xmlns='http://www.w3.org/2000/svg', version="1.1")
        marker = et.XML("""<defs><marker id="marker" viewBox="0 0 10 10" refX="7" refY="5" markerUnits="strokeWidth" orient="auto" markerWidth="4" markerHeight="5"> <polyline points="0,0 10,5 0,10 1,5" stroke="currentColor" /> </marker></defs>""")
        doc.append(marker)

        for n in viz_nodes.values():
            n.svg(doc)
            #et.SubElement(doc, "circle", cx=str(n.center_x()), cy=str(n.top()), r='3')

        # sorted list of arc lengths, to calculate the rank-length of each arc
        alens = list(sorted(set([a.length() for a in self.arcs])))

        #ArcViz = ArcVizDirColor
        for arc in self.arcs:
            a = ArcViz(arc, viz_nodes, d=alens.index(arc.length()))
            a.svg(doc)

        doc.attrib["width"] = str(max_x)
        doc.attrib["height"] = str(max_y + max_word_height)
        
        if as_obj:
            return doc
        else:
            return et.tostring(doc)
        #}}}

    @classmethod
    def from_pygraph(cls,graph):
        ret = cls()
        ret.add_node(node=DepTreeNode(form="ROOT",
                                      node_id= -1))
        for node in sorted(graph.nodes(),key=lambda n:n.minIndex()):
            ret.add_node(node=DepTreeNode(form=node.get_original_text(),
                                          node_id = node.uid))
        for (u,v) in graph.edges():
            ret.add_arc(arc=DepTreeArc(head_node_id=u.uid,
                                       mod_node_id=v.uid, 
                                       label=graph.edge_label((u,v))))
            
        return ret
    
    @classmethod
    def from_conll_str(self,conll_str,tags=False):
        lst = [x.strip().split() for x in strio.StringIO(conll_str.strip())]
        return self.from_conll_list(lst,tags)

    
     
    @classmethod
    def from_conll_list(self,conll_lst,tags=False):
        sent = [{'tag':tag,'id':nid,'form':form,'parent':par,'prel':rel} for \
                    nid,form,lemma,ctag,tag,morph,par,rel,_,_ in conll_lst]
        return self.from_conll_sent(sent)

    @classmethod
    def from_conll_sent(self,conll_sent,tags=False):
        arcs = []
        d = DepTreeVisualizer()
        d.add_node(DepTreeNode("-R-",0,"ROOT"))
        for tok in conll_sent:
            if tags:
                d.add_node(DepTreeNode(tok['form'],float(tok['id']),tok['tag']))
            else:
                d.add_node(DepTreeNode(tok['form'],float(tok['id']),None))
            if float(tok['parent']) != -1:
                arcs.append((float(tok['parent']),float(tok['id']),tok['prel']))
        for par,nid,rel in arcs:
            d.add_arc(DepTreeArc(par,nid,rel))
        return d

if __name__ == '__main__':
    
    d = DepTreeVisualizer.from_conll_str("""
1     Rolls-Royce     _     NN     NNP     _     4     NMOD     _     _
2     Motor     _     NN     NNP     _     4     NMOD     _     _
3     Cars     _     NN     NNPS     _     4     NMOD     _     _
4     Inc.     _     NN     NNP     _     5     SBJ     _     _
5     said     _     VB     VBD     _     0     ROOT     _     _
6  it _     PR     PRP     _     7     SBJ     _     _
7  expects     _     VB     VBZ     _     5     OBJ     _     _
8     its     _     PR     PRP$     _     10     NMOD     _     _
9     U.S.     _     NN     NNP     _     10     NMOD     _     _
10     sales     _     NN     NNS     _     12     SBJ     _     _
11     to     _     TO     TO     _     12     VMOD     _     _
12     remain     _     VB     VB     _     7     OBJ     _     _
13     steady     _     JJ     JJ     _     12     VMOD     _     _
14     at     _     IN     IN     _     12     ADV     _     _
15     about     _     IN     IN     _     17     NMOD     _     _
16     1,200     _     CD     CD     _     15     AMOD     _     _
17     cars     _     NN     NNS     _     14     PMOD     _     _
18     in     _     IN     IN     _     12     ADV     _     _
19     1990     _     CD     CD     _     18     PMOD     _     _
20     .     _     .     .     _     5     P     _     _ """)
    print "<div>",d.as_svg(compact=True,flat=True),"</div>"
  # print "<div>",d.as_svg(compact=False),"</div>"

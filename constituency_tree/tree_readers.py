import sexprs
import tree

import codecs
import re, sys

#### Generic tree readers

def read_trees_file(fh, extra_bracket=True):
   sxps = sexprs.read_as_stream(unicode(fh.read()))
   for s in sxps:
      if extra_bracket:
         yield tree.LingTree.from_sexpr(s[0])
      else:
         yield tree.LingTree.from_sexpr(s)

def read_trees_oneperline_file(fh, extra_bracket=True):
   for line in fh:
      if extra_bracket:
         yield tree.LingTree.from_str(unicode(line.strip()))
      else:
         yield tree.LingTree.from_str("(%s)" % unicode(line.strip()))

#### Heb
def read_hebtb2_file(fh):
   for t in read_trees_oneperline_file(fh,False):
      yield t

#### WSJ 
def read_wsj_file(fh):
   for t in read_trees_file(fh): yield t

#### FRENCH
def read_ftb_file(fh):
   for t in read_trees_file(fh): yield t

#### Penn BIO IE
def __pennbio_filter_comments(fh):
   for line in fh:
      if line and line[0] != ';': yield line
def __pennbio_remove_span_from_pos(pos):
   if pos.startswith("::"): return ":"
   return pos.split(":",1)[0]

def read_bioie_file(fh, keep_spans=False):
   content = unicode("".join(__pennbio_filter_comments(fh)))
   sxps = sexprs.read_as_stream(content)
   for s in sxps:
      t = tree.LingTree.from_sexpr(s)
      if not keep_spans:
         t.transform_pos(__pennbio_remove_span_from_pos)
      yield t

#### GENIA 
def read_genia_file(fh):
   """
   Assume one-tree-per-line
   """
   for line in fh:
      line = line.strip()
      line = re.sub(r"(\S+)/([^\s\)]+)",r"(\2 \1)",line)
      line = "(%s)" % line
      try:
         yield tree.LingTree.from_str(unicode(line))
      except KeyError: 
         sys.stderr.write("skipping bad tree: %s\n"%line)
   
if __name__=='__main__':
   base = "/Users/yoavg/Vork/Research/corpora/trees"
   # WSJ treeebank
   fh = codecs.open(base+"/WSJ/sec_00")
   trees = list(read_wsj_file(fh))
   print trees[0].as_tagged_sent()

   # pennBioIE
   fh = codecs.open(base+"/BIO/cyp/source_file_1000.mrg")
   trees = list(read_bioie_file(fh))
   print trees[0].as_tagged_sent()

   # genia
   fh = codecs.open(base+"/BIO/genia/tb-beta/GTB/91079577.tree")
   trees = list(read_genia_file(fh))
   print trees[0].as_tagged_sent()

   # heb tb
   fh = codecs.open(base+"/heb/tbv2gt/tbv2","r","utf8")
   trees = list(read_hebtb2_file(fh))
   print trees[0].as_tagged_sent()





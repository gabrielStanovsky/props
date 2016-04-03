# encoding: cp1255
import sexprs
import copy
import cPickle as pickle

# LingTree is a class representing a constituency tree/sub-tree
class LingTree:
   def __init__(self,name,childs,parent=None):

      self.childs = childs      # List of node's childs
      self.name = name          # Name of node's Tag
      self.parent = parent      # Node's parent

   def set_name(self, new_name): self.name = new_name
   def get_name(self) : return self.name
   def is_leaf(self): return False
   def get_cname(self): return self.name.split("-")[0]


   # Build Tree from string
   @classmethod
   def from_str(self, string):
      sexpr = sexprs.read(iter(string.strip()))
      return self.from_sexpr(sexpr[0])

   from_sexpr_static_counter = 0
   from_sexpr_static_counter_dep_id = 0
   @classmethod
   def from_sexpr(self,sexpr,start_id_count=True):
      if start_id_count:
          self.from_sexpr_static_counter = 0
          self.from_sexpr_static_counter_dep_id = 0
      if isinstance(sexpr,list) and len(sexpr) == 2 and isinstance(sexpr[0],unicode) and isinstance(sexpr[1],unicode):
         self.from_sexpr_static_counter += 1
         if tuple(sexpr)[0] == "-NONE-":
             return Leaf(tuple(sexpr),self.from_sexpr_static_counter,-1)
         else:
            self.from_sexpr_static_counter_dep_id += 1
            return Leaf(tuple(sexpr),self.from_sexpr_static_counter,self.from_sexpr_static_counter_dep_id)
      elif isinstance(sexpr, list):
         t = LingTree(sexpr[0], [LingTree.from_sexpr(c,False) for c in sexpr[1:]])
         for child in t.childs: child.parent = t
         return t
      else:
         import sys
         sys.stderr.write("%s\n" % sexpr.encode("utf8"))
         sys.stderr.write( "Error!\n" )
         raise Error
      
   # return list represents the tree (Recursively), the first element is the node and the rest elements are node's childs
   def as_lists(self):
      return [self.get_name()] +[cl.as_lists() for cl in self.childs]

   def write(self, fh):
      d = self.as_lists()
      pickle.dump(d,fh,1)

   @classmethod
   def read(self, fh):
      d = pickle.load(fh)
      t = LingTree.from_sexpr(d)
      return t

   # returns string represents the tree
   def __str__(self):
      return "(%s: %s)" % (self.get_name(), map(lambda x:x.get_name(),self.childs))

   # returns list of node's leafs
   def collect_leaves(self,ignore_empties=True):
      for child in self.childs:
         for leaf in child.collect_leaves(ignore_empties):
            yield leaf

   # returns begin and end indexes of the subtree (relative to the root of the tree)
   def get_leaves_indexes(self):
       leaves = list(self.collect_leaves(False))
       return leaves[0].dep_id , leaves[-1].dep_id

   # returns the sentence represented by the tree
   def as_words(self):
      return " ".join(l.get_word() for l in self.collect_leaves(True))

   def apply_to_leaves(self, func, ignore_empties=True):
      """
      replace all leafs with func(leaf)
      """
      for leaf in self.collect_leaves(ignore_empties):
         leaf.replace_with(func(leaf))

   def transform_pos(self, pos_transformer):
      """
      pos_transformer: a function from string to string to be applied on all
      POStag strings
      """
      self.apply_to_leaves(lambda leaf:Leaf.from_str(u"((%s %s))" % (pos_transformer(leaf.get_pos()), leaf.get_word()))) 

   def transform_word(self, word_transformer):
      """
      word_transformer: a function from string to string to be applied on all
      word(lexical) strings
      """
      self.apply_to_leaves(lambda leaf:Leaf.from_str(u"((%s %s))" % (leaf.get_pos(), word_transformer(leaf.get_word())))) 

   def transform_pos_word(self, pw_transformer):
      """
      pw_transformer: a function from (str,str) to (str,str) to be applied on all
      (pos,word) strings
      """
      self.apply_to_leaves(lambda leaf:Leaf.from_str(u"((%s %s))" % (pw_transformer(leaf.get_pos(), leaf.get_word())))) 
      
   def as_sexpr(self):
      return "(%s %s)" % (self.get_name(), "".join([x.as_sexpr() for x in self.childs]))

   def as_bact_sexpr(self):
      return "(%s%s)" % (self.get_name(), "".join([x.as_bact_sexpr() for x in self.childs]))

   def as_ghkmrule_lhs(self):
      return "%s(%s)" % (self.get_name(), " ".join([x.as_ghkmrule_lhs() for x in self.childs]))

   def replace_with(self,new_tree):
      #print "replacing with",new_tree.as_sexpr()
      new_tree=copy.deepcopy(new_tree)
      parent = self.parent
      if parent:
         for x,child in enumerate(parent.childs):
            if child == self:
               #print "replacing",child.as_sexpr()
               parent.childs[x] = new_tree
      self = new_tree
      new_tree.parent = parent
      return new_tree

   def extract_rules(self):
      """
      Return a list of (lhs,rhs) pairs, where 'lhs' is a string and 'rhs' a tuple of strings
      """
      yield (self.get_name(), tuple([c.get_name() for c in self.childs]))
      for c in self.childs:
         for rule in c.extract_rules():
            yield rule
   
   def extract_lexical_rules(self):
      for c in self.childs:
         for rule in c.extract_lexical_rules():
            yield rule

   def as_sent(self):
      sent = []
      for leaf in self.collect_leaves():
         sent.append(leaf.value[1])
      return u" ".join(sent)

   def as_tagged_sent(self):
      sent = []
      for leaf in self.collect_leaves():
         sent.append("%s/%s" % (leaf.value[1], leaf.value[0]))
      return u" ".join(sent)

   def as_postags_sequence(self):
      sent = []
      for leaf in self.collect_leaves():
         sent.append(leaf.get_pos())
      return sent

   def as_bitpar_input(self, known_words=None):
      sent = []
      for leaf in self.collect_leaves():
         w = leaf.value[1]
         if known_words is not None and (w not in known_words): w = "@@UNK@@"
         sent.append(w)
      return "\n".join(sent)

   def apply_to_nodes(self, func):
      func(self)
      for c in self.childs: c.apply_to_nodes(func)

   def apply_to_nodes_bu(self, func):
      for c in self.childs: c.apply_to_nodes(func)
      func(self)

   def transform_node(self, node_transformer):
      self.apply_to_nodes(node_transformer)

   def transform_node_bu(self, node_transformer):
      self.apply_to_nodes_bu(node_transformer)

   def remove(self):
      """
      Remove given node from the tree.
      If this results in a parent with no childrens, parent is removed as well.
      """
      parent = self.parent
      self.parent = None
      if parent == None: # removing the root of the tree, or an element that has already been removed
         return None
      parent.childs = [c for c in parent.childs if c!=self]
      if not parent.childs:
         parent.remove()

   def remove_empty_elements(self):
      for leaf in self.collect_leaves(ignore_empties=False):
         if leaf.is_empty():
            leaf.remove()
   def remove_punctuations(self):
      for leaf in self.collect_leaves(ignore_empties=False):
         if leaf.is_punct():
            leaf.remove()

   def search(self, predicate):
      if predicate(self): 
         yield self
      for c in self.childs:
         for res in c.search(predicate):
            yield res
   
def set_v_markovization():
   def vmarkov(self):
      if self.parent: parname = self.parent.name
      else: parname = "ROOT"
      return self.name + "~" + parname
   LingTree.get_name = vmarkov



# Leaf is a class representing a leaf in LingTree
class Leaf(LingTree):
   def __init__(self, value,id=0, dep_id=0):
      self.parent = None            # node's parent
      self.value = list(value)      # pos-tag and word
      self.name = self.value[0]     # pos-tag
      self.id = id
      self.dep_id = dep_id

   def is_leaf(self): return True
   def get_name(self): return self.get_pos()
   def get_cname(self): return self.get_cpos()

   def get_word(self): return self.value[1]
   def get_pos(self): return self.value[0]
   def get_cpos(self): 
      return self.value[0].split('-',1)[0]
   def get_features(self):
      try:
         return self.value[0].split('-',1)[1]
      except IndexError: return ''

   def set_word(self,w): self.value[1]=w
   def set_pos(self,pos): 
      if pos[-1]=='-': pos = pos[:-1]
      self.value[0] = pos
   def set_cpos(self,cpos): 
      new_pos = "-".join([cpos, self.get_features()])
      self.set_pos(new_pos)
   def set_features(self,features):
      new_pos = "-".join([self.get_cpos(), features])
      self.set_pos(new_pos)

   def apply_to_nodes(self, func):
      func(self)

   def as_sexpr(self):
      return "(%s %s)" % (self.value[0],self.value[1])

   def as_bact_sexpr(self):
      return "(%s(%s))" % (self.value[0],self.value[1])

   def as_ghkmrule_lhs(self):
      return "%s(%s)" % (self.value[0],self.value[1])

   def as_lists(self):
      return list(self.value)

   def __str__(self): return str(self.value)
   def collect_leaves(self,ignore_empties=True): 
      if ignore_empties:
         if self.is_empty():
            return []
      return [self]

   def is_empty(self):
      return self.value[1] in [u'*PRO*',u'*T*',u'*NONE*'] or self.value[0] in [u'-NONE-']

   def is_punct(self):
      return self.get_pos().startswith("yy")

   def extract_rules(self):
      for x in []: yield x

   def extract_lexical_rules(self):
      yield (tuple((self.value[1], self.value[0])))

   def search(self, predicate):
      if predicate(self): yield self

def from_str(s):
   return LingTree.from_str(unicode(s))

def read_from_filenames_onetreeperline(fs,double_paren=False):
   for f in fs:
      for line in file(f):
         line = line.strip()
         if not double_paren: line = "(%s)" % line
         yield f,LingTree.from_str(unicode(line))

def read_from_filenames_sexprs(fs,double_paren=False):
   import codecs
   for f in fs:
      data = iter(codecs.open(f,encoding="utf-8").read())
      for sexpr in sexprs.read_as_stream(data):
         yield f, LingTree.from_sexpr(sexpr)


__t = u"""
 (
 (S
    (PP-LOC (IN Under)
      (NP (DT these) (NNS conditions) ))
    (, ,)
    (NP-SBJ
      (NP
        (NP (RB even) (DT a) (VBG flattening) (IN out) )
        (PP (IN of)
          (NP (JJ economic) (NN growth) ))
        (PRN (: --) (`` ``)
          (S-NOM
            (NP-SBJ (-NONE- *) )
            (VP (VBG catching)
              (NP (NN cold) )))
          ('' '') (: --) )
        (PP-LOC (IN in)
          (NP (DT the) (JJ healthy) (JJ metropolitan) (NNS areas) ))))
    (VP (MD will)
      (VP (VB create)
        (NP
          (NP (JJ significant) (NNS opportunities) )
          (PP (IN for)
            (NP
              (NP
                (NP (NNS corporations) )
                (CC and)
                (NP (JJ professional) (NN service) (NNS firms) ))
              (VP (VBG looking)
                (PP-CLR (IN for)
                  (NP (NNS bargains) ))
                (SBAR-TMP (IN as)
                  (S
                    (NP-SBJ (DT the) (NN realestate) (NN industry) )
                    (VP (VBZ catches)
                      (NP (NN pneumonia) ))))))))))
    (. .) ))
"""


if __name__ == '__main__':
   t =LingTree.from_str(__t)
   l = t.as_lists()


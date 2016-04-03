def _tokenizer(stream):
   stack = []
   for item in stream:
      if item in ["(",")"]:
         if stack: yield "".join(stack)
         stack = []
         yield item
      elif item in [' ',"\n","\r","\t"]: 
         if stack: yield "".join(stack)
         stack = []
      else:
         stack.append(item)
   if stack: yield "".join(stack)

def sexprs_reader(stream):
   #print "entering sexpr_reader"
   current = []
   for next in stream: 
      if next == '(':
         current.append(sexprs_reader(stream))
      elif next == ')':
         #print "leaving sexpr_reader",current
         return current
      else: # next is a symbol
         current.append(next)
   #print "at_end"
   return current

def sexpr_reader(stream):
   """
   kept only for backward compatability.
   """
   return sexprs_reader(stream)[0]

def read(stream):
   return sexpr_reader(_tokenizer(stream))

def read_as_stream(stream):
   for sexp in sexprs_reader(_tokenizer(stream)):
      yield sexp

def to_string(sexpr):
   if isinstance(sexpr,list): 
      return "( %s )" % " ".join([to_string(sxp) for sxp in sexpr])
   else:
      return sexpr
   

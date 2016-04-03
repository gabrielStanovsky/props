# Pharse based function tags indicating adverbials (Collins 97)
ADVERBIALS = ["ADV", "VOC", "BNF", "DIR", "EXT", "LOC", "MNR", "TMP", "CLR","PRP"]


#utils - returns index in first list
any_in = lambda a, b: [i for i,x in enumerate(a) if x in b]
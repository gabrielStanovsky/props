from nltk.corpus.reader.propbank import PropbankSplitTreePointer
def is_raising(pb_instance):
    for arg in pb_instance.arguments:
        if isinstance(arg[0], PropbankSplitTreePointer):
            return True
    return False


if __name__ == "__main__":
    from nltk.corpus import propbank
    pb_instances = propbank.instances()[:9353] 
    inst = pb_instances[3]
    t = inst.tree
    pred = inst.predicate.select(t)
    
    

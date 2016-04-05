import os
from pygraph.classes.digraph import digraph
from props.applications.run import load_berkeley, parseSentences
from props.graph_representation.word import NO_INDEX


class BratAttribute:
    counter = 0
    @staticmethod
    def get_attribute(label, wordInd):
        BratAttribute.counter += 1
        return '[ "A{0}", "{1}", "W{2}" ],'.format(BratAttribute.counter, label, wordInd)
    


class BratVisualizer:
    def __init__(self):
        self.visualize_html = open(BASE_PATH + './html/visualize.html').read() 
    
    def to_html(self, gr):
        sent = gr.originalSentence
        entities, relations = gr.getJson()
        ret = self.visualize_html.replace('SENTENCE_STUB', sent.replace('"', '\\"'))
        ret = ret.replace('ENTITIES_STUB', '\n'.join(["['W{0}', '{1}', [[{2}, {3}]]],".format(uid, self.get_label(d), d['charIndices'][0], d['charIndices'][1]) 
                                                      for uid, d in entities.items()]))
        
        ret = ret.replace('ATTRIBUTES_STUB', '\n'.join([self.get_attributes(uid, d) 
                                                      for uid, d in entities.items()]))
        
        ret = ret.replace('RELATIONS_STUB', '\n'.join(["['R{0}', '{1}', [['head', 'W{2}'], ['dep', 'W{3}']]],".format(i, rel, head, dep) 
                                                       for i, (head, dep, rel) in enumerate(relations)]))
        
        
        
        
        return ret
    
    def get_attributes(self, uid, d):
        ret = []
        feats = d['feats']
        featList = ['tense', 'passive']
        if not d['predicate']:
            featList.append('definite')
        for feat in featList:
            if feats[feat]:
                ret.append(BratAttribute.get_attribute(feats[feat], uid))
        return ''.join(ret)
    
    def get_label(self, d):
        feats = d['feats']
        pos = d['feats']['pos']
        
        if feats['implicit']: 
            return ' '.join([w.word for w in feats['text']])
        if d['predicate']:
            return 'Predicate'
        else: 
            return pos
    
BASE_PATH = os.path.join(os.path.dirname(__file__), '../')

if __name__ == "__main__":
    b = BratVisualizer()
    sent = 'Barack Obama, the US president, landed in Hawaii.'
    load_berkeley(True)
    gs = parseSentences(sent)
    g,tree = gs[0]
    page = b.to_html(g)
    page = page.replace('PROPOSITIONS_STUB', '<br>'.join([str(prop) for prop in g.getPropositions('html')]))
    with open('/home/gabis/test/tmp.htm', 'w') as fout:
        fout.write(page)

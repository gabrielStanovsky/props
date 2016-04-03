import unittest
from props.unit_tests.props_test import PropsTest


class SanityTest(PropsTest):
    ''' installation tests '''
    def test_sanity(self):
        testCases = [
         ('Barack Obama, the US president, just came back from Russia.',
'''Barack Obama , the US president , just came back from Russia .
103    2,Obama;1,Barack    NNP    0    0    sameAs_arg,105;subj,18
104    5,US;6,president        0    0    sameAs_arg,105;subj,18
105    2,SameAs        1    1    
18    9,came    VBD    1    1    
24    8,just    RB    0    0    mod,18
26    10,back    RB    0    0    mod,18
27    12,Russia    NNP    0    0    prep_from,18''',
),
                     ('She said that the boy is tall',
'''
She said that the boy is tall
146    2,said    VBD    1    1    
147    1,She    PRP    0    0    subj,146
151    5,boy    NN    0    0    prop_of,153
153    7,tall    VBZ    1    0    comp,146
'''
),
                     
                     ('If you build it, they will come',
'''If you build it , they will come
215    3,build    VBP    1    0    condition,216
216    1,If    IN    1    1    
217    2,you    PRP    0    0    subj,215
218    8,come    VB    1    0    outcome,216
219    4,it    PRP    0    0    dobj,215
221    6,they    PRP    0    0    subj,218'''           
)]
        
        for sent, expected in testCases:
            self.compare(self.getProps(sent), expected)
            
        
if __name__ == '__main__':
    unittest.main()
    
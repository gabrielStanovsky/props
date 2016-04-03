from pygraph.classes.digraph import digraph
import file_handling
# Import the module and instantiate a graph object
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.minmax import minimal_spanning_tree
from pygraph.algorithms.minmax import shortest_path
from pygraph.algorithms.accessibility import accessibility
gr = digraph()
# Add nodes
gr.add_nodes(['X','Y','Z','A','P','B','C','D','E'])
 
# Add edges
gr.add_edge(('X','Y'),wt=1)
gr.add_edge(('X','Z'),wt=1)
gr.add_edge(('Z','X'),wt=1)
# gr.add_edge(('Z','A'),wt=1)
gr.add_edge(('Y','P'),wt=1)
d = shortest_path(gr, 'A')

gr.add_edge(('A','B'))
gr.add_edge(('B','C'))
gr.add_edge(('C','D'))
gr.add_edge(('D','E'))

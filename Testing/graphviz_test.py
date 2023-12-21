import graphviz

g = graphviz.Digraph('G', filename='hello.gv')

g.edge('Hello', 'World')

g.view()
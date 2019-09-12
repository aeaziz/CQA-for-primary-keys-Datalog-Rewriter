from graph import *


# Class representing a M-Graph
class MGraph(Graph):

    def __init__(self, t):
        super(MGraph, self).__init__(t)

    # As the Vertex may not be hashable, we need an unique representation for each atom that will be used as key
    def id_vertex(self, vertex):
        return vertex.name

    # Computes the links as they are defined in the article
    def generate(self):
        k_q_cons = self.q.k_q_cons()
        for atom1 in self.q.body.atoms:
            self.vertex.append(atom1)
            self.edges[atom1.name] = []
            for atom2 in [value for value in self.q.body.atoms if value != atom1]:
                contained = True
                vars1_closure = k_q_cons.closure(atom1.get_variables())
                for var in atom2.get_key_variables():
                    if var not in vars1_closure:
                        contained = False
                if contained:
                    self.edges[atom1.name].append(atom2)

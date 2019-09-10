from graph import *


# Graph used to compute sequential proofs. Vertex are variables or set of variables that are useful.
class FGraph(Graph):

    def __init__(self, t):
        self.label = {}
        super(FGraph, self).__init__(t)

    # As the Vertex may not be hashable, we need an unique representation for each atom that will be used as key
    def id_vertex(self, vertex):
        if type(vertex) == list:
            return repr(vertex)
        else:
            return vertex

    # We create an edge between A and B if there's some atom F where A belongs to Key(F) and B belongs to Vars(F)
    def generate(self):
        for r in self.q.fd.set:
            for fd in self.q.fd.set[r]:
                if len(fd.left) > 1:
                    string_left = repr(fd.left)
                    v = fd.left
                else:
                    string_left = fd.left[0]
                    v = fd.left[0]
                if v not in self.vertex:
                    self.vertex.append(v)
                    self.edges[string_left] = []
                    self.label[string_left] = {}
                if fd.right not in self.vertex:
                    self.vertex.append(fd.right)
                    self.edges[fd.right] = []
                    self.label[fd.right] = {}
                self.edges[string_left].append(fd.right)
                if fd.right not in self.label[string_left]:
                    self.label[string_left][fd.right] = []
                self.label[string_left][fd.right].append(r)

    # We compute sequential proofs by finding paths in our graph.
    def find_sequential_proofs(self):
        seq_proofs = []
        for v1 in self.vertex:
            for v2 in [v for v in self.vertex if v != v1]:
                paths = self.find_paths(v1, v2)
                for path in paths:
                    sp = []
                    for i in range(0, len(path) - 1):
                        sp.append(self.label[self.id_vertex(path[i])][self.id_vertex(path[i + 1])])
                    seq_proofs.append((v1, v2, sp))
        return seq_proofs

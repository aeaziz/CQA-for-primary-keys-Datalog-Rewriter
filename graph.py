__metaclass__ = type


# Class representing a generic graph
class Graph:
    def __init__(self, q):
        self.q = q
        self.vertex = []
        self.edges = {}
        self.generate()

    def generate(self):
        pass

    # As the Vertex may not be hashable, we need an unique representation for each atom that will be used as key
    def id_vertex(self, vertex):
        pass

    # Finds all the paths between 2 vertex
    def find_paths(self, u, d):
        all_paths = []
        visited = {}
        for vertex in self.vertex:
            visited[self.id_vertex(vertex)] = False
        self.find_paths_rec(u, d, visited, [], all_paths)
        return all_paths

    # Recursive function used by find_paths
    def find_paths_rec(self, u, d, visited, path, all_paths):
        visited[self.id_vertex(u)] = True
        path.append(u)

        if u == d:
            all_paths.append(path[:])
        else:
            for i in self.edges[self.id_vertex(u)]:
                if not visited[self.id_vertex(i)]:
                    self.find_paths_rec(i, d, visited, path, all_paths)

        path.pop()
        visited[self.id_vertex(u)] = False

    # Finds all the cycles in the graph
    def find_cycles(self):
        cycles = []
        for vertex in self.vertex:
            for n in self.edges[self.id_vertex(vertex)]:
                paths = self.find_paths(n, vertex)
                for path in paths:
                    cycle = Cycle([vertex] + path)
                    if cycle not in cycles:
                        cycles.append(cycle)
        return cycles

    # Removes a vertex from the graph
    def remove_vertex(self, o):
        self.vertex.remove(o)
        del self.edges[self.id_vertex(o)]

    # True if the given strongly connected component is initial
    def is_initial(self, scc):
        l = list(scc)
        for v in self.vertex:
            for a in self.edges[self.id_vertex(v)]:
                if self.id_vertex(a) in l and self.id_vertex(v) not in l:
                    return False
        return True

    # Returns a list containing all the initial strongly connected components
    def strongly_initial_connected_components(self):
        sccs = self.strongly_connected_components()
        sicc = []
        for scc in sccs:
            if self.is_initial(scc) and len(scc)>0:
                sicc.append(scc)
        return  sicc

    # Returns a list containing all the strongly connected components
    def strongly_connected_components(self):
        identified = set()
        stack = []
        index = {}
        boundaries = []

        for v in self.vertex:
            if self.id_vertex(v) not in index:
                to_do = [('VISIT', v)]
                while to_do:
                    operation_type, v = to_do.pop()
                    if operation_type == 'VISIT':
                        index[self.id_vertex(v)] = len(stack)
                        stack.append(self.id_vertex(v))
                        boundaries.append(index[self.id_vertex(v)])
                        to_do.append(('POSTVISIT', v))
                        # We reverse to keep the search order identical to that of
                        # the recursive code;  the reversal is not necessary for
                        # correctness, and can be omitted.
                        to_do.extend(
                            reversed([('VISITEDGE', w) for w in self.edges[self.id_vertex(v)]]))
                    elif operation_type == 'VISITEDGE':
                        if self.id_vertex(v) not in index:
                            to_do.append(('VISIT', v))
                        elif self.id_vertex(v) not in identified:
                            while index[self.id_vertex(v)] < boundaries[-1]:
                                boundaries.pop()
                    else:
                        # operation_type == 'POSTVISIT'
                        if boundaries[-1] == index[self.id_vertex(v)]:
                            boundaries.pop()
                            scc = set(stack[index[self.id_vertex(v)]:])
                            del stack[index[self.id_vertex(v)]:]
                            identified.update(scc)
                            yield scc


# Class representing a cycle in a graph
class Cycle:
    def __init__(self, path):
        self.path = path

    def __eq__(self, other):
        for vertex in self.path:
            if vertex not in other.path:
                return False
        for vertex in other.path:
            if vertex not in self.path:
                return False
        return True

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return self.__str__()

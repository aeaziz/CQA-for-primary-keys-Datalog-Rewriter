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

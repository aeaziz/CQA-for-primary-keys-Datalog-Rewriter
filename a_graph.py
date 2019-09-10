from graph import *
from datalog import *


# Class representing an attack graph
class AttackGraph(Graph):
    def __init__(self, t):
        super(AttackGraph, self).__init__(t)

    # As the Atom class in not hashable, we need an unique representation for each atom that will be used as key
    def id_vertex(self, vertex):
        return vertex.name

    # To generate the graph, we compute the edges as they are defined in the articles
    def generate(self):
        for atom in self.q.body.atoms:
            self.vertex.append(atom)
            self.edges[atom.name] = []
            variables = set(atom.get_variables())
            attacked = []
            plus = self.compute_plus(atom)
            # Direct Links
            for other in [value for value in self.q.body.atoms if value != atom]:
                other_variables = set(other.get_variables())
                inter = variables.intersection(other_variables)
                inter = inter - set(plus)
                if inter:
                    attacked.append(other)
            # Indirect Links
            size = 0
            current = attacked
            while size != len(attacked):
                size = len(attacked)
                news = []
                for a in current:
                    for o in [value for value in self.q.body.atoms if value not in attacked and value != atom]:
                        inter = set(a.get_variables()).intersection(set(o.get_variables()))
                        inter = inter - set(plus)
                        if inter:
                            attacked.append(o)
                            news.append(o)
                current = news

            for other in attacked:
                self.edges[atom.name].append(other)

    # For an atom F, it computes F+q
    def compute_plus(self, atom):
        if atom.consistent:
            new = self.q.fd
        else:
            new = self.q.fd.without_atom(atom)
        return new.closure(atom.get_key_variables())

    # Checks if the attack from atom1 to atom2 is weak
    def attack_is_weak(self, atom1, atom2):
        closure = self.q.fd.closure(atom1.get_key_variables())
        for var in atom2.get_key_variables():
            if var not in closure:
                return False
        return True

    # Checks if a given cycle is weak ie all the attacks inside the cycle are weak
    def cycle_is_weak(self, cycle):
        for i in range(0, len(cycle.path) - 1):
            if not self.attack_is_weak(cycle.path[i], cycle.path[i + 1]):
                return False
        return True

    # Checks if all the cycles on the graph are weak
    def all_cycles_weak(self):
        cycles = self.find_cycles()
        for cycle in cycles:
            if not self.cycle_is_weak(cycle):
                return False
        return True

    # Returns the atoms that are not attacked
    def not_attacked(self):
        attacked = set()
        not_attacked = []
        for atom in self.vertex:
            for a in self.edges[atom.name]:
                attacked.add(a.name)
        for atom in self.vertex:
            if atom.name not in attacked:
                not_attacked.append(atom)
        return not_attacked

    # Returns the atoms that attacks a given atom
    def attacks(self, atom):
        attacks = []
        for r in self.vertex:
            if atom in self.edges[self.id_vertex(r)]:
                attacks.append(r)
        return attacks

    # Returns all the atoms that attacks a given variable
    def attacks_variable(self, var):
            atom = Atom("N")
            atom.add_variable(var, True)
            self.q.body.add_atom(atom)
            self.q.fd.set[atom.name] = []
            a_graph = AttackGraph(self.q)
            self.q.body.remove_atom(atom)
            del self.q.fd.set[atom.name]
            return a_graph.attacks(atom)


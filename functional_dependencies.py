from f_graph import *


# Represents a functional dependency
class FD:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + " --> " + str(self.right)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(self.__str__())


# Represents the set of functional dependencies of a query (Only primary-keys)
class FDSet:
    def __init__(self, q):
        self.set = {}
        self.q = q

    # Adds a given FD
    def add_fd(self, source, fd):
        self.set[source].append(fd)

    # For an atom R, it computes the set of functional dependencies of q\{R}
    def without_atom(self, atom):
        new = FDSet(self.q)
        new.set = self.set.copy()
        del new.set[atom.name]
        return new

    # Computes the closure of a set of variables
    def closure(self, var):
        closure = var[:]
        size = 0
        while len(closure) != size:
            size = len(closure)
            for r in self.set:
                for fd in self.set[r]:
                    if all(v in closure for v in fd.left) and fd.right not in closure:
                        closure.append(fd.right)
        return closure

    # Finds atoms F that contains all the variables in z
    def find_f(self, z):
        atoms = []
        for atom in self.q.body.atoms:
            if set(z).issubset(set(atom.get_variables())):
                atoms.append(atom)
        return atoms

    # Checks if a FD is internal to the query
    def is__internal_fd(self, sp):
        if len(self.find_f(sp.fd.left)) == 0:
            return False
        variables = set(sp.fd.left).union(sp.fd.right)
        banned_relations = []
        for variable in variables:
            banned_relations = banned_relations + self.q.a_graph.attacks_variable(variable)
        for step in sp.proof:
            ok = False
            for r in step:
                atom = self.q.body.get_atom(r)
                if atom not in banned_relations:
                    ok = True
            if not ok:
                return False
        return True

    # Finds the set of FD that are internal to the query
    def find_internal_fd(self):
        ifd = []
        f_graph = FGraph(self.q)
        sps = f_graph.find_sequential_proofs()
        for (v1, v2, p) in sps:
            sp = SequentialProof(v1, v2, p)
            if self.is__internal_fd(sp):
                ifd.append(sp.fd)
        return ifd

    def __str__(self):
        return str(self.set)

    def __repr__(self):
        return self.__str__()


# Class representing a Sequential Proofs
class SequentialProof:
    def __init__(self, v1, v2, p):
        value1 = v1
        if type(value1) is not list:
            value1 = [value1]
        self.fd = FD(value1, v2)
        self.proof = p

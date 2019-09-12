from a_graph import *
from m_graph import *
from datalog import *
from functional_dependencies import *
from saturator import *
from weak_cycle_delete import *
from fo_rewrite import *


# Structure that takes a string query as input and parses it into a set of FD and the body of a Datalog query
# It also keeps the status of the rewriting (New rules index, frozen variables, graphs, etc..)
class TranslateInput:
    def __init__(self):
        self.fd = FDSet(self)
        self.body = DatalogBody()
        self.a_graph = None
        self.f_graph = None
        self.frozen = []
        self.query_index = 0

    # Adds an atom
    def add_atom(self, atom):
        self.body.add_atom(atom)
        self.generate_fd_set()
        self.generate_attack_graph()

    # Removes an atom
    def remove_atom(self, atom):
        self.body.remove_atom(atom)
        self.generate_fd_set()
        self.generate_attack_graph()

    # Generates the set of FD
    def generate_fd_set(self):
        self.fd = FDSet(self)
        for atom in self.body.atoms:
            self.fd.set[atom.name] = []
            key = atom.get_key_variables()
            for var in atom.get_variables():
                self.fd.add_fd(atom.name, FD(key, var))

    # Generates the attack graph
    def generate_attack_graph(self):
        self.a_graph = AttackGraph(self)

    # Generates the F graph
    def generate_f_graph(self):
        self.f_graph = FGraph(self)

    # The variable becomes a constant
    def freeze_variable(self, var):
        self.body.freeze_variable(var)
        self.generate_fd_set()
        self.frozen.append(var)

    # Returns the FDSet representing K(q_cons)
    def k_q_cons(self):
        k_q_cons = self.fd
        for atom in self.body.atoms:
            if not atom.consistent:
                k_q_cons = k_q_cons.without_atom(atom)
        return k_q_cons

    # Checks if the query is saturated
    def is_saturated(self):
        internal_fd = self.fd.find_internal_fd()
        k_q_cons = self.k_q_cons()
        for fd in internal_fd:
            if fd.right not in k_q_cons.closure(fd.left):
                return False
        return True

    # Checks if all the atoms of the given cycle are in the given initial strong component
    def in_initial_strong_component(self, cycle, s):
        for a in cycle.path[:-1]:
            if a.name not in s:
                return False
        return True

    # Checks if the given cycle belongs to an initial strong component in the attack graph
    def is_initial_strong_component(self, cycle):
        sicc = self.a_graph.strongly_initial_connected_components()
        for s in sicc:
            if self.in_initial_strong_component(cycle, s):
                return True
        return False

    # Translates the query
    def translate(self):
        res = []
        if not self.is_saturated():
            s = Saturator(self)
            res = res + s.saturate()
        if self.a_graph.all_cycles_weak():
            while len(self.a_graph.vertex) > 0:
                not_attacked = self.a_graph.not_attacked()
                if len(not_attacked) > 0:
                    rewrite_fo(self, not_attacked[0], len(self.a_graph.vertex) > 1, res)
                    self.remove_atom(not_attacked[0])
                else:
                    m = MGraph(self)
                    cycles = m.find_cycles()
                    i = 0
                    cycle = cycles[i]
                    while not self.is_initial_strong_component(cycle):
                        i += 1
                        cycle = cycles[i]
                    delete_weak_cycle(self, cycle, res)
            return res
        else:
            print("The problem is Co-NPHard")

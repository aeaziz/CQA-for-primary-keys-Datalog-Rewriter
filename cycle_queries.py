from datalog import *

# To understand this functions and classes, please read the formulas in the article

def fill_atom_xi_vali(atom_fill, cycle, valuations, start_rel, start_val, n):
    for i in range(0, n):
        atom = cycle.path[start_rel + i]
        fill_atom_x_val(atom, atom_fill, valuations[start_val + i])


def fill_atom_x_val(atom, atom_fill, valuation, key=False):
    for var in atom.get_key_values():
        if var in atom.get_variables():
            atom_fill.add_variable(valuation[var], key)
        else:
            atom_fill.add_constant(var, key)


def fill_atom_x(atom, atom_fill, key=False):
    for var in atom.get_key_values():
        if var in atom.get_variables():
            atom_fill.add_variable(var, key)
        else:
            atom_fill.add_constant(var, key)


def generate_qi(query_fill, cycle, valuations):
    for val in valuations:
        fill_query_q_vali(query_fill, cycle, val)


def fill_query_q_vali(query_fill, cycle, valuation):
    for atom in cycle.path[:-1]:
        new = Atom(atom.name)
        for value in atom.content:
            if value in atom.get_variables():
                new.add_variable(valuation[value], False)
            else:
                new.add_constant(value, False)
        query_fill.add_atom(new)


class RelevantQuery(DatalogQuery):
    def __init__(self, atom, cycle):
        head = Atom("Relevant_" + atom.name)
        for value in atom.content:
            head.add_variable(value, False)
        super(RelevantQuery, self).__init__(head)
        for atom in cycle.path[:-1]:
            self.add_atom(atom)


class DirectGarbageQuery(DatalogQuery):
    def __init__(self, atom, relevant):
        head = Atom("Garbage_" + atom.name)
        super(DirectGarbageQuery, self).__init__(head)
        neg_call = relevant.head
        neg_call.negative = True
        for var in atom.content:
            if var in atom.get_key_values():
                head.add_variable(var, False)
        self.add_atom(atom)
        self.add_atom(neg_call)


class RelevantGarbageQuery(DatalogQuery):
    def __init__(self, cycle, atom1, atom2, garbage1, garbage2):
        head = garbage1.head
        super(RelevantGarbageQuery, self).__init__(head)
        for atom in cycle.path[:-1]:
            self.add_atom(atom)
        self.add_atom(garbage2.head)


class PKQuery(DatalogQuery):
    def __init__(self, cycle, valuations, cycle_code):
        head = Atom("Pk_" + cycle_code)
        super(PKQuery, self).__init__(head)
        k = len(cycle.path) - 1
        # Construct head
        fill_atom_xi_vali(head, cycle, valuations, 0, 0, k)
        fill_atom_x_val(cycle.path[0], head, valuations[k])
        # Construct q0, q1, ..
        generate_qi(self, cycle, valuations[:k + 1])
        # Construct x1(1) = x1(0), x2(2) = x2(1), ..
        v = 1
        for atom in cycle.path[1:]:
            for value in atom.get_key_variables():
                e = EqualityAtom(valuations[v][value], valuations[v - 1][value])
                self.add_atom(e)
            v = v + 1
        # Construct x0(0) != x0(k)
        for var in cycle.path[0].content:
            if var in cycle.path[0].get_key_variables():
                i = EqualityAtom(valuations[0][var], valuations[k][var])
                i.inequality = True
                self.add_atom(i)


class BaseDConQuery(DatalogQuery):
    def __init__(self, cycle, valuations, sp1, cycle_code):
        head = Atom("DCon_" + cycle_code)
        super(BaseDConQuery, self).__init__(head)
        k = len(cycle.path) - 1
        # Construct head and recursive atom
        first = cycle.path[0]
        fill_atom_x_val(first, head, sp1)
        fill_atom_x_val(first, head, sp1)
        fill_atom_xi_vali(head, cycle, valuations, 1, 1, k - 1)

        fill_query_q_vali(self, cycle, sp1)

        # Construct PK atom
        pk = Atom("Pk_" + cycle_code)
        fill_atom_xi_vali(pk, cycle, valuations, 0, 0, k)
        fill_atom_x_val(first, pk, valuations[k])
        self.add_atom(pk)


class RecDConQuery(DatalogQuery):
    def __init__(self, cycle, valuations, sp1, sp2, cycle_code):
        head = Atom("DCon_" + cycle_code)
        super(RecDConQuery, self).__init__(head)
        k = len(cycle.path) - 1
        rec = Atom("DCon_" + cycle_code)
        self.add_atom(rec)
        # Construct head and recursive atom
        first = cycle.path[0]
        fill_atom_x_val(first, head, valuations[0])
        fill_atom_x_val(first, head, sp1)
        fill_atom_xi_vali(head, cycle, valuations, 1, 1, k - 1)
        fill_atom_x_val(first, rec, valuations[0])
        fill_atom_x_val(first, rec, sp2)
        fill_atom_xi_vali(rec, cycle, valuations, 1, 1, k - 1)

        # Construct PK atom
        pk = Atom("Pk_" + cycle_code)
        fill_atom_x_val(first, pk, sp2)
        fill_atom_xi_vali(pk, cycle, valuations, 1, k + 1, k - 1)
        fill_atom_x_val(first, pk, sp1)
        self.add_atom(pk)

        # Construct inequalities atoms
        for i in range(1, k):
            atom = cycle.path[i]
            for var in atom.content:
                if var in atom.get_key_variables():
                    ie = EqualityAtom(valuations[k + i][var], valuations[i][var])
                    ie.inequality = True
                    self.add_atom(ie)


class InLongDCycleQuery(DatalogQuery):
    def __init__(self, cycle, valuations, cycle_code):
        head = Atom("InLongDCycle_" + cycle_code)
        super(InLongDCycleQuery, self).__init__(head)
        k = len(cycle.path) - 1
        for i in range(0, k):
            atom = cycle.path[i]
            for var in atom.get_key_values():
                if var in atom.get_variables():
                    head.add_variable(valuations[i][var], False)
                else:
                    head.add_constant(var, False)

        pk = Atom("Pk_" + cycle_code)
        dcon = Atom("DCon_" + cycle_code)
        self.add_atom(pk)
        self.add_atom(dcon)
        # Construct head and recursive atom
        first = cycle.path[0]
        fill_atom_xi_vali(pk, cycle, valuations, 0, 0, k)
        fill_atom_x_val(first, pk, valuations[k])
        fill_atom_x_val(first, dcon, valuations[k])
        fill_atom_xi_vali(dcon, cycle, valuations, 0, 0, k)


class GarbageLonQuery(DatalogQuery):
    def __init__(self, atom, body):
        head = Atom("Garbage_" + atom.name)
        for var in atom.get_key_values():
            if var in atom.get_variables():
                body.add_variable(var, False)
                head.add_variable(var, False)
            else:
                body.add_constant(var, False)
                head.add_constant(var, False)
        super(GarbageLonQuery, self).__init__(head)
        self.add_atom(body)


class KeepQuery(DatalogQuery):
    def __init__(self, atom):
        head = Atom("Keep_" + atom.name)
        super(KeepQuery, self).__init__(head)
        for var in atom.content:
            if var in atom.get_variables():
                head.add_variable(var, False)
            else:
                head.add_constant(var, False)
        self.add_atom(atom)
        gs = Atom("Garbage_" + atom.name)
        gs.negative = True
        for var in atom.get_key_values():
            if var in atom.get_variables():
                gs.add_variable(var, False)
            else:
                gs.add_constant(var, False)
        self.add_atom(gs)


class LinkQuery(DatalogQuery):
    def __init__(self, cycle, valuations, i, cycle_code):
        head = Atom("Link_" + cycle_code)
        val = valuations[0]
        super(LinkQuery, self).__init__(head)
        # Construct Head
        for var in cycle.path[0].get_key_values():
            if var in cycle.path[0].get_variables():
                head.add_variable(var, False)
            else:
                head.add_constant(var, False)
        for var in cycle.path[0].get_key_values():
            if var in cycle.path[0].get_variables():
                head.add_variable(val[var], False)
            else:
                head.add_constant(var, False)

        # Construct keep atoms
        for atom in cycle.path[:-1]:
            new = Atom("Keep_" + atom.name)
            for var in atom.content:
                if var in atom.get_variables():
                    new.add_variable(var, False)
                else:
                    new.add_constant(var, False)
            self.add_atom(new)
        for atom in cycle.path[:-1]:
            new = Atom("Keep_" + atom.name)
            for var in atom.content:
                if var in atom.get_variables():
                    new.add_variable(val[var], False)
                else:
                    new.add_constant(var, False)
            self.add_atom(new)

        # Construct equality atoms
        for var in cycle.path[i].get_key_variables():
            if var in cycle.path[i].get_variables():
                eq = EqualityAtom(var, val[var])
                self.add_atom(eq)


class Trans1Query(DatalogQuery):
    def __init__(self, cycle, sp1, cycle_code):
        first = cycle.path[0]
        head = Atom("Trans_" + cycle_code)
        super(Trans1Query, self).__init__(head)
        fill_atom_x(first, head)
        fill_atom_x_val(first, head, sp1)
        l = Atom("Link_" + cycle_code)
        fill_atom_x(first, l)
        fill_atom_x_val(first, l, sp1)
        self.add_atom(l)


class Trans2Query(DatalogQuery):
    def __init__(self, cycle, sp1, sp2, cycle_code):
        first = cycle.path[0]
        head = Atom("Trans_" + cycle_code)
        super(Trans2Query, self).__init__(head)
        fill_atom_x(first, head)
        fill_atom_x_val(first, head, sp1)
        t = Atom("Trans_" + cycle_code)
        fill_atom_x(first, t)
        fill_atom_x_val(first, t, sp2)
        self.add_atom(t)
        l = Atom("Link_" + cycle_code)
        fill_atom_x_val(first, l, sp2)
        fill_atom_x_val(first, l, sp1)
        self.add_atom(l)


class Trans3Query(DatalogQuery):
    def __init__(self, cycle, sp1, sp2, cycle_code):
        first = cycle.path[0]
        head = Atom("Trans_" + cycle_code)
        super(Trans3Query, self).__init__(head)
        fill_atom_x(first, head)
        fill_atom_x_val(first, head, sp2)
        t = Atom("Trans_" + cycle_code)
        fill_atom_x(first, t)
        fill_atom_x_val(first, t, sp1)
        self.add_atom(t)
        l = Atom("Link_" + cycle_code)
        fill_atom_x_val(first, l, sp2)
        fill_atom_x_val(first, l, sp1)
        self.add_atom(l)


class IdQuery(DatalogQuery):
    def __init__(self, cycle, valuations, cycle_code):
        head = Atom("IdentifiedBy_" + cycle_code)
        super(IdQuery, self).__init__(head)
        first = cycle.path[0]
        fill_atom_x(first, head)
        fill_atom_xi_vali(head, cycle, valuations, 0, 0, 1)

        for var in first.get_key_variables():
            a = Atom("Trans_" + cycle_code)
            fill_atom_x(first, a)
            fill_atom_x_val(first, a, valuations[2])
            m = MinAtom(valuations[2][var], a, valuations[0][var])
            self.add_atom(m)
        link = Atom("Link_" + cycle_code)
        fill_atom_x(first, link)
        fill_atom_x_val(first, link, valuations[1])
        self.add_atom(link)


class TQuery(DatalogQuery):
    def __init__(self, cycle, sp1, cycle_code):
        head = Atom("T_" + cycle_code)
        super(TQuery, self).__init__(head)
        first = cycle.path[0]
        fill_atom_x_val(first, head, sp1, True)
        for atom in cycle.path[:-1]:
            k = Atom("Keep_" + atom.name)
            for var in atom.content:
                if var in atom.get_variables():
                    head.add_variable(var, False)
                    k.add_variable(var, False)
                else:
                    head.add_constant(var, False)
                    k.add_constant(var, False)
            self.add_atom(k)
        i = Atom("IdentifiedBy_" + cycle_code)
        fill_atom_x(first, i)
        fill_atom_x_val(first, i, sp1)
        self.add_atom(i)


class NQuery(DatalogQuery):
    def __init__(self, atom, cycle, sp1, cycle_code):
        first = cycle.path[0]
        head = Atom("N_" + atom.name)
        head.consistent = True
        super(NQuery, self).__init__(head)
        fill_atom_x(atom, head, True)
        fill_atom_x_val(first, head, sp1)
        t = Atom("T_" + cycle_code)
        fill_atom_x_val(first, t, sp1)
        for atom in cycle.path[:-1]:
            for var in atom.content:
                if var in atom.get_variables():
                    t.add_variable(var, False)
                else:
                    t.add_constant(var, False)
        self.add_atom(t)

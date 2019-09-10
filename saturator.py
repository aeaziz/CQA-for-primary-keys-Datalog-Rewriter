from datalog import Atom, DatalogQuery, EqualityAtom


class Saturator:
    def __init__(self, to):
        self.to = to

    # For a FD Z -> w, generates a query N_index([Z],w) that makes explicit Z->w
    def gen_n_query(self, fd, index):
        n = Atom("N_" + str(index))
        n.set_consistent(True)
        for var in fd.left:
            n.add_variable(var, True)
        n.add_variable(fd.right, False)
        n_query = DatalogQuery(n)
        for atom in self.to.body.atoms:
            n_query.add_atom(atom)
        return n_query

    # For an atom F, for a FD Z->w, generates a queries that removes the blocks that can be removed
    def gen_sat_atom(self, f, fd):
        new_head = Atom("SAT_" + f.name)
        for value in f.content:
            if f.is_variable[f.content.index(value)]:
                new_head.add_variable(value, False)
            else:
                new_head.add_constant(value, False)
        new_query = DatalogQuery(new_head)
        new_query.add_atom(f)

        remove_query = self.gen_remove_block(f, fd)
        new_query.add_atom(remove_query.head)
        return new_query, remove_query

    # For an atom F, for a FD Z->w, generates a query that removes the blocks that can be removed
    def gen_remove_block(self, f, fd):
        can_be_removed = Atom("REMOVE_BLOCK_" + f.name)
        can_be_removed.negative = True
        for v in f.get_variables():
            if f.is_key[f.content.index(v)]:
                can_be_removed.add_variable(v, False)
        query = DatalogQuery(can_be_removed)
        eqs = []
        ok = []
        ineq = None
        for atom in self.to.body.atoms:
            query.add_atom(atom)
        for atom in self.to.body.atoms:
            new = Atom(atom.name)
            for i in range(0, len(atom.content)):
                value = atom.content[i]
                if atom.is_variable[i]:
                    new_value = value
                    i = 0
                    while new_value in atom.get_variables():
                        new_value = value + str(i)
                        i = i = 1
                    if value not in ok:
                        if value in fd.left:
                            eqs.append(EqualityAtom(value, new_value))
                        if value in fd.right:
                            ineq = EqualityAtom(value, new_value, True)
                        ok.append(value)

                    new.add_variable(new_value, atom.is_key[i])
                else:
                    new.add_constant(value, atom.is_key[i])
            query.add_atom(new)
        for eq in eqs:
            query.add_atom(eq)
        query.add_atom(ineq)

        return query

    def saturate(self):
        queries = []
        to_remove = []
        to_add = []
        n_index = 0
        for fd in self.to.fd.find_internal_fd():
            n_query = self.gen_n_query(fd, n_index)
            n_index = n_index + 1

            fs = self.to.fd.find_f(fd.left)
            for f in fs:
                if f not in to_remove:
                    to_remove.append(f)
                n_query.body.remove_atom(f)

                new_query, query = self.gen_sat_atom(f, fd)

                if query not in queries:
                    queries.append(query)
                if new_query not in queries:
                    queries.append(new_query)
                to_add.append(new_query.head)
                n_query.add_atom(new_query.head)

            to_add.append(n_query.head)
            queries.append(n_query)
        for f in to_remove:
            self.to.remove_atom(f)
        for f in to_add:
            self.to.add_atom(f)
        return queries

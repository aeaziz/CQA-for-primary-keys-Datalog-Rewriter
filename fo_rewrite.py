from datalog import *


# Computes the values to be used
def calculate_values(atom):
    # V
    v = atom.get_variables()
    # X
    x = atom.get_key_variables()
    # Y
    y = atom.get_not_key_values()
    # Z
    z = ["Z_" + str(j) for j in range(0, len(y))]
    z_re = [False for i in range(0, len(z))]
    # C
    c = []
    for j in range(0, len(y)):
        if y[j] in atom.get_constants() or y[j] in x or y[j] in y[:j]:
            c.append(EqualityAtom(z[j], y[j]))
            z_re[j] = True

    atom_with_z = Atom(atom.name)
    atom_with_z_re = Atom(atom.name)
    for var in atom.get_key_values():
        if var in atom.get_variables():
            atom_with_z.add_variable(var, True)
            atom_with_z_re.add_variable(var, True)
        else:
            atom_with_z.add_constant(var, True)
            atom_with_z_re.add_constant(var, True)
    for var_z in z:
        atom_with_z.add_variable(var_z, False)
        if z_re[z.index(var_z)]:
            atom_with_z_re.add_variable(var_z, False)
        else:
            atom_with_z_re.add_variable(y[z.index(var_z)], False)

    return v, x, y, z, z_re, atom_with_z, atom_with_z_re, c


# Rewrites an atom in Datalog using the FO Logic formula : For some v, R(x,y) and For all z, R(x,z) -> C and rec_call
def rewrite_fo(t, atom, has_next, res=[], atoms_done=[]):
    res.append("% Rewriting of " + str(atom))
    v, x, y, z, z_re, atom_with_z, atom_with_z_re, c = calculate_values(atom)
    q1 = construct_first_query(t, atom, atoms_done, x)
    res.append(q1)

    if has_next or len(c) > 0:
        if atom.consistent and has_next:
            next_head = Atom("R_" + str(t.query_index + 1))
            for var in t.frozen:
                next_head.add_variable(var, False)
            q1.add_atom(next_head)
            atoms_done.append(atom)
            t.query_index = t.query_index + 1
        elif not atom.consistent:
            q2 = construct_second_query(t, atom_with_z, atoms_done, v, z, z_re)
            q3 = construct_third_query(t, atoms_done, c, z, z_re, atom_with_z_re)
            q1.add_atom(q2.head)
            res.append(q2)
            res.append(q3)
            if has_next:
                next_head = Atom("R_" + str(t.query_index + 3))
                for var in t.frozen:
                    next_head.add_variable(var, False)
                q3.add_atom(next_head)
                atoms_done.append(atom)
                t.query_index = t.query_index + 3
    else:
        t.query_index = t.query_index + 1


# Generates a query implementing the fragment "For some v, R(x,y)"
def construct_first_query(t, atom, atoms_done, x):
    # For some V, R(x,y) ...
    head = Atom("R_" + str(t.query_index))
    for var in t.frozen:
        head.add_variable(var, False)
    q1 = DatalogQuery(head)
    for a in atoms_done:
        q1.add_atom(a)
    q1.add_atom(atom)
    for var in x:
        if var not in t.frozen:
            t.freeze_variable(var)
    return q1


# Generates a query implementing the fragment "For all z, R(x,z) ->"
def construct_second_query(t, atom_with_z, atoms_done, v, z, z_re):
    # For all Z, R(x,z) -> ...
    head = Atom("R_" + str(t.query_index + 1))
    head.negative = True
    for var in t.frozen:
        head.add_variable(var, False)

    q2 = DatalogQuery(head)
    for atom in atoms_done:
        q2.add_atom(atom)
    q2.add_atom(atom_with_z)

    head_next = Atom("R_" + str(t.query_index + 2))
    head_next.negative = True

    for var in t.frozen:
        head_next.add_variable(var, False)
    for var in z:
        if not z_re[z.index(var)]:
            head_next.add_variable(var, False)
    for var in v:
        if var not in t.frozen:
            t.freeze_variable(var)
    for var in z:
        if z_re[z.index(var)]:
            head_next.add_variable(var, False)

    q2.add_atom(head_next)
    return q2


# Generates a query implementing the fragment "C and rec_call"
def construct_third_query(t, atoms_done, c, z, z_re, atom_with_z_re):
    head = Atom("R_" + str(t.query_index + 2))
    for var in t.frozen:
        head.add_variable(var, False)
    for var in z:
        if z_re[z.index(var)]:
            head.add_variable(var, False)
    q3 = DatalogQuery(head)
    for atom in atoms_done:
        q3.add_atom(atom)
    q3.add_atom(atom_with_z_re)
    for ea in c:
        q3.add_atom(ea)
    return q3

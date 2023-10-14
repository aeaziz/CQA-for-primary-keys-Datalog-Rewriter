from data_structures import Atom, ConjunctiveQuery, AtomValue, EqualityAtom, DatalogQuery
from typing import List, Set, Dict


'''
This module is used to handle rewritings that can be expressed in first order logic.
These functions follow the following formula to rewrite a sjfBCQ q:

Let A(X,Y) be a non attacked atom where X is the key of A.

(1)    For some X:
(2)        For some Y:
(3)            A(X,Y)
(4)        AND
(5)        For every Z:
(6)            If A(X,Z) then :
(7)                C and rewriting of q\{A}
            
Where C is a set of constraints over Z.

The query produced by existential_query() expresses lines (1)-(4).
The query produced by forall_query() expresses the negation of line (5-6).
the query produced by cond_and_continue_query expresses the line (7)

Note that in some cases lines (5-7) may not be necessary.
'''


def rewrite_fo(q: ConjunctiveQuery, atom: Atom, atoms_done: Set[Atom], initial_index: int):
    """
    Rewrites a non attacked atom from a query q in Datalog
    """
    res = existential_query(q, atom, atoms_done, initial_index)
    atoms_done.add(atom)
    for var in atom.variables():
        q.freeze_variable(var)
    return res


def generate_z_variables(n: int) -> List[AtomValue]:
    """
    Generates n temporal variables
    :param n:   The number of variables to be generated
    :return:    A list containing n variables
    """
    res = []
    for i in range(0, n):
        res.append(AtomValue("Z_" + str(i), True))
    return res


def existential_query(q: ConjunctiveQuery, atom: Atom, atoms_done: Set[Atom], initial_index: int) -> List[DatalogQuery]:
    """
    Generates the 'existential' query needed for the first order logic rewriting
    :param q:   Query being rewritten
    :param atom:    Atom being rewritten
    :param atoms_done:  Atoms that are already rewritten
    :param initial_index:   Index used to numerate queries
    :return:    A list containing the 'existential' query (and potentially the 'forall' and 'cond and continue' queries)
    """

    head = Atom("R_" + str(initial_index), q.frozen_vars)
    eq = DatalogQuery(head)
    for a_d in atoms_done:
        eq.add_atom(a_d)
    eq.add_atom(atom)
    if len(set(q.content.keys()) - set(atoms_done)) > 1 or len(set(atom.variables())) != len(atom.content):
        next_head = Atom(
            "R_" + str(initial_index + 1),
            q.frozen_vars + [var for var in q.get_key_vars(atom) if var not in q.frozen_vars]
        )
        eq.add_atom(next_head, True)
        return [eq] + forall_query(q, atom, atoms_done, initial_index + 1)
    return [eq]


def forall_query(q: ConjunctiveQuery, atom: Atom, atoms_done: Set[Atom], initial_index: int) -> List[DatalogQuery]:
    """
    Generates the 'forall' query needed for the first order logic rewriting
    :param q:   Query being rewritten
    :param atom:    Atom being rewritten
    :param atoms_done:  Atoms that are already rewritten
    :param initial_index:   Index used to numerate queries
    :return:    A list containing the 'forall' query (and potentially the 'cond and continue' query)
    """
    head = Atom(
        "R_" + str(initial_index),
        q.frozen_vars + [var for var in q.get_key_vars(atom) if var not in q.frozen_vars]
    )
    faq = DatalogQuery(head)
    for a_d in atoms_done:
        faq.add_atom(a_d)
    y_values = q.get_not_key(atom)
    z_vars = generate_z_variables(len(y_values))
    z_atom = Atom(atom.name, [value for value in q.get_key(atom)] + z_vars)
    faq.add_atom(z_atom)

    c = {}
    needed = False
    for i in range(len(y_values)):
        if not y_values[i].var or y_values[i] in y_values[:i] or y_values[i] in q.get_key(atom):
            c[z_vars[i]] = y_values[i]
            needed = True

    next_head = Atom(
        "R_" + str(initial_index + 1),
        q.frozen_vars + [var for var in q.get_key_vars(atom) if var not in q.frozen_vars] + z_vars
    )
    faq.add_atom(next_head, True)
    if needed:
        return [faq] + cond_and_continue_query(q, atom, atoms_done, initial_index + 1, c)
    else:
        return [faq]


def cond_and_continue_query(q: ConjunctiveQuery, atom: Atom, atoms_done: Set[Atom], initial_index: int,
                            c: Dict[AtomValue, AtomValue]) -> List[DatalogQuery]:
    """
    Generates the 'cond and continue' query needed for the first order logic rewriting
    :param q:   Query being rewritten
    :param atom:    Atom being rewritten
    :param atoms_done:  Atoms that are already rewritten
    :param initial_index:   Index used to numerate queries
    :param c:   A set of constraints represented by a Dict
    :return:    A list containing the 'forall' query
    """
    y_values = q.get_not_key(atom)
    z_vars = generate_z_variables(len(y_values))
    head_content = []
    for i in range(len(y_values)):
        if y_values[i].var and y_values[i] not in y_values[:i] and y_values[i] not in q.get_key(atom) and \
                y_values[i] not in q.frozen_vars:
            head_content.append(y_values[i])
        else:
            head_content.append(z_vars[i])
    head = Atom(
        "R_" + str(initial_index),
        q.frozen_vars + [var for var in q.get_key_vars(atom) if var not in q.frozen_vars] + head_content
    )

    cacq = DatalogQuery(head)
    for a_d in atoms_done:
        cacq.add_atom(a_d)
    z_atom = Atom(atom.name, q.get_key_vars(atom) + head_content)
    cacq.add_atom(z_atom)
    for val in c:
        cacq.add_atom(EqualityAtom(val, c[val]))
    if len(set(q.content.keys()) - set(atoms_done)) > 1:
        atom_vars = atom.variables()
        next_head = Atom(
            "R_" + str(initial_index + 1),
            q.frozen_vars + [atom_vars[i] for i in range(len(atom_vars)) if atom_vars[i] not in atom_vars[:i]]
        )
        cacq.add_atom(next_head, False)
    return [cacq]

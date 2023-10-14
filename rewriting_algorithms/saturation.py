from data_structures import ConjunctiveQuery, FunctionalDependency, Atom, AtomValue, EqualityAtom, DatalogQuery
from algorithms import generate_valuations, apply_valuation_to_atom_values, apply_valuation_to_atom
from typing import FrozenSet, List, Dict

"""
This module is used to handle the saturation of a non saturated query.
Let q be a non saturated query q.
The non saturation of q means that there are some FD Z -> w such that:
    - Z -> w is internal
    - q_cons do not imply Z -> w

The saturation process is the following:
    1)

"""


def apply_valuation_to_atom(atom: Atom, valuation: Dict[AtomValue, AtomValue]):
    return Atom(atom.name, apply_valuation_to_atom_values(atom.content, valuation))


def saturate(q: ConjunctiveQuery, bad_fd: FrozenSet[FunctionalDependency]):
    queries = []
    n_index = 0
    for fd in bad_fd:
        concerned_atoms = [atom for atom in q.get_atoms() if fd.left.issubset(set(atom.variables()))]
        for atom in concerned_atoms:
            rem_query = remove_block_query(atom, q, fd)
            new_a_query = new_atom_query(atom, q)
            atom_fd = q.get_atom_fd(atom)
            atom_is_key = q.content[atom][1]
            atom_consistent = q.content[atom][2]
            q.remove_atom(atom)
            q.add_atom(Atom("SAT_" + atom.name, atom.content), atom_fd, atom_is_key, atom_consistent)
            queries.append(rem_query)
            queries.append(new_a_query)

    for fd in bad_fd:
        variables = list(fd.left)
        is_key = [True for i in range(len(variables))] + [False]
        variables.append(fd.right)
        n_q = n_query(q, variables, n_index)
        queries.append(n_q)
        q.add_atom(Atom("N_" + str(n_index), variables), frozenset([fd]), is_key, True)
        n_index = n_index + 1
    return queries


def remove_block_query(atom: Atom, q: ConjunctiveQuery, fd: FunctionalDependency):
    head = Atom("REMOVE_" + atom.name, q.get_key_vars(atom))
    remove_query = DatalogQuery(head)
    valuations = generate_valuations(2, q.get_all_variables())
    for var in q.get_key_vars(atom):
        valuations[0][var] = var
        valuations[1][var] = var
    for atom in q.get_atoms():
        remove_query.add_atom(apply_valuation_to_atom(atom, valuations[0]))
        remove_query.add_atom(apply_valuation_to_atom(atom, valuations[1]))
    for var in fd.left - set(q.get_key_vars(atom)):
        remove_query.add_atom(EqualityAtom(valuations[0][var], valuations[1][var]))
    remove_query.add_atom(EqualityAtom(valuations[0][fd.right], valuations[1][fd.right], True))
    return remove_query


def new_atom_query(atom: Atom, q: ConjunctiveQuery):
    head = Atom("SAT_" + atom.name, atom.content)
    sat = DatalogQuery(head)
    sat.add_atom(atom)
    sat.add_atom(Atom("REMOVE_" + atom.name, q.get_key_vars(atom)), True)
    return sat


def n_query(q: ConjunctiveQuery, variables: List[AtomValue], n_index: int):
    head = Atom("N_" + str(n_index), variables)
    n_q = DatalogQuery(head)
    for atom in q.get_atoms():
        n_q.add_atom(atom)
    return n_q

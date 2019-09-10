from datalog import DatalogQuery, DatalogBody, Atom, MinAtom, EqualityAtom
from cycle_queries import *


def find_all_variables_in_cycle(cycle):
    variables = []
    for atom in cycle.path[:-1]:
        for value in atom.content:
            if value in atom.get_variables() and value not in variables:
                variables.append(value)
    return variables


def generate_n_valuations(variables, n):
    valuations = []
    for i in range(0, int(n)):
        valuations.append({})
    for variable in variables:
        start = 0
        renames = [variable for d in range(0, int(n))]
        while not all([rename not in variables for rename in renames]):
            start = start + 1
            for i in range(0, int(n)):
                renames[i] = variable + str(start + i)
        for i in range(0, int(n)):
            valuations[i][variable] = renames[i]

    return valuations


def delete_weak_cycle(t, cycle, res):
    variables = find_all_variables_in_cycle(cycle)
    k = len(cycle.path) - 1
    valuations = generate_n_valuations(variables, 2 * k + 2)
    sp1 = valuations[-2]
    sp2 = valuations[-1]
    valuations = valuations[:-2]
    cycle_code = cycle.path[0].name
    for atom in cycle.path[1:-1]:
        cycle_code += atom.name

    construct_relevant_queries(cycle, res)
    construct_pk_query(cycle, res, valuations, cycle_code)
    construct_base_dcon_query(cycle, res, valuations, sp1, cycle_code)
    construct_rec_dcon_query(cycle, res, valuations, sp1, sp2, cycle_code)
    construct_in_long_cycle_query(cycle, res, valuations, cycle_code)

    construct_long_garbage_queries(cycle, res, cycle_code)
    construct_keep_queries(cycle, res)
    construct_link_queries(cycle, res, valuations, cycle_code)
    construct_trans_queries(cycle, res, sp1, sp2, cycle_code)
    construct_id_query(cycle, res, valuations, cycle_code)
    construct_t_query(cycle, res, sp1, cycle_code)
    t_atom = res[-1].head
    construct_n_queries(cycle, res, sp1, cycle_code)
    i = -1
    current = res[i]
    n_atoms = []
    while current.head != t_atom:
        n_atoms.append(current.head)
        i = i - 1
        current = res[i]
    for atom in cycle.path[:-1]:
        t.remove_atom(atom)
    t.add_atom(t_atom)
    for n in n_atoms:
        t.add_atom(n)
    t.generate_attack_graph()


def construct_relevant_queries(cycle, res):
    relevant = {}
    garbage = {}
    relevantGarbage = {}
    for atom in cycle.path[:-1]:
        relevant[atom.name] = RelevantQuery(atom, cycle)
        garbage[atom.name] = DirectGarbageQuery(atom, relevant[atom.name])
    for atom1 in cycle.path[:-1]:
        for atom2 in [value for value in cycle.path[:-1] if value != atom1]:
            relevantGarbage[atom1.name] = RelevantGarbageQuery(cycle, atom1, atom2, garbage[atom1.name],
                                                               garbage[atom2.name])
    res.append("% Captures facts with zero outdegree, belonging to a block containing a garbage fact")
    for q in relevant:
        res.append(relevant[q])
    for q in garbage:
        res.append(garbage[q])
    res.append("% Captures facts belonging to relevant 1-embeddings containing a garbage fact")
    for q in relevantGarbage:
        res.append(relevantGarbage[q])


def construct_pk_query(cycle, res, valuations, cycle_code):
    res.append("% Captures facts belonging to a n-embedding")
    res.append(PKQuery(cycle, valuations, cycle_code))


def construct_rec_dcon_query(cycle, res, valuations, sp1, sp2, cycle_code):
    res.append(RecDConQuery(cycle, valuations, sp1, sp2, cycle_code))


def construct_base_dcon_query(cycle, res, valuations, sp1, cycle_code):
    res.append(BaseDConQuery(cycle, valuations, sp1, cycle_code))


def construct_in_long_cycle_query(cycle, res, valuations, cycle_code):
    res.append(InLongDCycleQuery(cycle, valuations, cycle_code))


def construct_long_garbage_queries(cycle, res, cycle_code):
    res.append("% All facts belonging to a n-embedding must be in the maximal garbage-set")
    body = Atom("InLongDCycle_" + cycle_code)
    for atom in cycle.path[:-1]:
        res.append(GarbageLonQuery(atom, body))


def construct_keep_queries(cycle, res):
    res.append("% We keep only facts that are not in the garbage set")
    for atom in cycle.path[:-1]:
        res.append(KeepQuery(atom))


def construct_link_queries(cycle, res, valuations, cycle_code):
    k = len(cycle.path) - 1
    for i in range(0, k):
        res.append(LinkQuery(cycle, valuations, i, cycle_code))


def construct_trans_queries(cycle, res, sp1, sp2, cycle_code):
    res.append(Trans1Query(cycle, sp1, cycle_code))
    res.append(Trans2Query(cycle, sp1, sp2, cycle_code))
    res.append(Trans3Query(cycle, sp1, sp2, cycle_code))


def construct_id_query(cycle, res, valuations, cycle_code):
    res.append(IdQuery(cycle, valuations, cycle_code))


def construct_t_query(cycle, res, sp1, cycle_code):
    res.append(TQuery(cycle, sp1, cycle_code))


def construct_n_queries(cycle, res, sp1, cycle_code):
    for atom in cycle.path[:-1]:
        res.append(NQuery(atom, cycle, sp1, cycle_code))

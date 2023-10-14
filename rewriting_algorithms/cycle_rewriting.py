from data_structures import Atom, ConjunctiveQuery, AtomValue, DatalogQuery, EqualityAtom, CompareAtom, \
    FunctionalDependency
from algorithms import generate_valuations, apply_valuation_to_atom, apply_valuation_to_atom_values
from typing import List, Tuple


def rewrite_cycle(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> List[DatalogQuery]:
    queries = relevant_queries(cycle)
    queries = queries + relevant_garbage_queries(cycle, q)
    queries = queries + embed_garbage_queries(cycle, q)
    queries.append(pk_query(cycle, q, rewriting_index))
    queries.extend(dcon_queries(cycle, q, rewriting_index))
    queries.append(inLongDCycle_query(cycle, q, rewriting_index))
    queries = queries + cycle_garbage_queries(cycle, q)
    queries = queries + keep_queries(cycle, q)
    queries = queries + link_queries(cycle, q, rewriting_index)
    queries.extend(trans_queries(cycle, q, rewriting_index))
    queries = queries + id_queries(cycle, q, rewriting_index)
    queries.append(t_query(cycle, q, rewriting_index))
    queries = queries + n_queries(cycle, q, rewriting_index)

    new_keys = []
    for var in q.get_key_vars(cycle[0]):
        new_keys.append(AtomValue("K_" + var.name, True))

    for atom in cycle:
        key_vars = q.get_key_vars(atom)
        n_atom = Atom("N_" + atom.name, key_vars + new_keys)
        fds = []
        for var in new_keys:
            fds.append(FunctionalDependency(frozenset(key_vars), var))
        is_key = [True for i in range(len(key_vars))] + [False for i in range(len(new_keys))]
        q.add_atom(n_atom, frozenset(fds), is_key, True)
        q.remove_atom(atom)
    variables = get_cycle_vars(cycle)

    t_atom = Atom("T_" + str(rewriting_index), new_keys + variables)
    fds = []
    for var in variables:
        fds.append(FunctionalDependency(frozenset(new_keys), var))
    is_key = [True for i in range(len(key_vars))] + [False for i in range(len(variables))]
    q.add_atom(t_atom, frozenset(fds), is_key, False)

    return queries


def get_cycle_vars(cycle: List[Atom]) -> List[AtomValue]:
    all_vars = []
    for atom in cycle:
        for var in atom.variables():
            if var not in all_vars:
                all_vars.append(var)
    return all_vars


def relevant_queries(cycle: List[Atom]) -> List[DatalogQuery]:
    queries = []
    for atom in cycle:
        query = DatalogQuery(Atom("Rlvant_" + atom.name, atom.content))
        for all_atom in cycle:
            query.add_atom(all_atom)
        queries.append(query)
    return queries


def relevant_garbage_queries(cycle: List[Atom], q: ConjunctiveQuery) -> List[DatalogQuery]:
    queries = []
    for atom in cycle:
        query = DatalogQuery(Atom("Garbage_" + atom.name, q.get_key_vars(atom)))
        query.add_atom(atom)
        query.add_atom(Atom("Rlvant_" + atom.name, atom.content), True)
        queries.append(query)
    return queries


def embed_garbage_queries(cycle: List[Atom], q: ConjunctiveQuery):
    queries = []
    for atom in cycle:
        for other in cycle:
            if atom != other:
                query = DatalogQuery(Atom("Garbage_" + atom.name, q.get_key_vars(atom)))
                for a in cycle:
                    query.add_atom(a)
                query.add_atom(Atom("Garbage_" + other.name, q.get_key_vars(other)))
                queries.append(query)
    return queries


def pk_query(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> DatalogQuery:
    all_vars = get_cycle_vars(cycle)
    k = len(cycle)
    valuations = generate_valuations(k + 1, all_vars)
    head_content = []
    for i in range(len(cycle)):
        head_content = head_content + apply_valuation_to_atom_values(q.get_key_vars(cycle[i]), valuations[i])
    head_content = head_content + apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), valuations[k])
    head = Atom("Pk_" + str(rewriting_index), head_content)
    query = DatalogQuery(head)
    for i in range(0, k + 1):
        for atom in q.get_atoms():
            query.add_atom(apply_valuation_to_atom(atom, valuations[i]))
    for i in range(1, k):
        atom = cycle[i]
        for var in q.get_key_vars(atom):
            query.add_atom(EqualityAtom(valuations[i][var], valuations[i - 1][var]))
    for var in q.get_key_vars(cycle[0]):
        query.add_atom(EqualityAtom(valuations[k][var], valuations[k - 1][var]))
    for var in q.get_key_vars(cycle[0]):
        query.add_atom(EqualityAtom(valuations[0][var], valuations[k][var], True))
    return query


def dcon_queries(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> Tuple[DatalogQuery, DatalogQuery]:
    k = len(cycle)
    all_vars = get_cycle_vars(cycle)
    valuations = generate_valuations(2 * k + 2, all_vars)
    sp1 = valuations[0]
    sp2 = valuations[1]
    valuations = valuations[2:]

    valuation_0_0 = apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), valuations[0])
    valuation_k_0 = apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), valuations[k])
    sp1_0 = apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), sp1)
    sp2_0 = apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), sp2)
    from_1_to_k_1 = []
    from_k_1_to_2k_1 = []
    for i in range(1, k):
        from_1_to_k_1 = from_1_to_k_1 + apply_valuation_to_atom_values(q.get_key_vars(cycle[i]), valuations[i])
        from_k_1_to_2k_1 = from_k_1_to_2k_1 + apply_valuation_to_atom_values(q.get_key_vars(cycle[i]),
                                                                             valuations[k + i])

    rec_head_content = valuation_0_0 + sp1_0 + from_1_to_k_1
    base_head_content = sp1_0 + sp1_0 + from_1_to_k_1
    rec_content = valuation_0_0 + sp2_0 + from_1_to_k_1
    rec_pk_content = sp2_0 + from_k_1_to_2k_1 + sp1_0
    base_pk_content = valuation_0_0 + from_1_to_k_1 + valuation_k_0

    rec_head = Atom("DCon_" + str(rewriting_index), rec_head_content)
    rec_query = DatalogQuery(rec_head)
    rec_query.add_atom(Atom("DCon_" + str(rewriting_index), rec_content))
    rec_query.add_atom(Atom("Pk_" + str(rewriting_index), rec_pk_content))
    for i in range(1, k):
        valued_1 = apply_valuation_to_atom_values(q.get_key_vars(cycle[i]), valuations[k + i])
        valued_2 = apply_valuation_to_atom_values(q.get_key_vars(cycle[i]), valuations[i])
        for j in range(len(valued_1)):
            rec_query.add_atom(EqualityAtom(valued_1[j], valued_2[j], True))

    base_head = Atom("DCon_" + str(rewriting_index), base_head_content)
    base_query = DatalogQuery(base_head)
    for atom in q.get_atoms():
        base_query.add_atom(apply_valuation_to_atom(atom, sp1))
    base_query.add_atom(Atom("Pk_" + str(rewriting_index), base_pk_content))

    return rec_query, base_query


def inLongDCycle_query(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> DatalogQuery:
    k = len(cycle)
    all_vars = get_cycle_vars(cycle)
    valuations = generate_valuations(k + 1, all_vars)
    valuation_k_0 = apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), valuations[k])
    from_0_to_k_1 = []
    for i in range(0, k):
        from_0_to_k_1 = from_0_to_k_1 + apply_valuation_to_atom_values(q.get_key_vars(cycle[i]), valuations[i])

    query = DatalogQuery(Atom("InLongDCycle_" + str(rewriting_index), from_0_to_k_1))
    pk_content = from_0_to_k_1 + valuation_k_0
    dcon_content = valuation_k_0 + from_0_to_k_1
    query.add_atom(Atom("Pk_" + str(rewriting_index), pk_content))
    query.add_atom(Atom("DCon_" + str(rewriting_index), dcon_content))

    return query


def cycle_garbage_queries(cycle: List[Atom], q: ConjunctiveQuery) -> List[DatalogQuery]:
    queries = []
    for atom in cycle:
        query = DatalogQuery(Atom("Garbage_" + atom.name, q.get_key_vars(atom)))
        query.add_atom(Atom("InLongDCycle", get_cycle_vars(cycle)))
        queries.append(query)
    return queries


def keep_queries(cycle: List[Atom], q: ConjunctiveQuery) -> List[DatalogQuery]:
    queries = []
    for atom in cycle:
        query = DatalogQuery(Atom("Keep_" + atom.name, atom.variables()))
        query.add_atom(atom)
        query.add_atom(Atom("Garbage_"+atom.name, q.get_key_vars(atom)), True)
        queries.append(query)
    return queries


def link_queries(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> List[DatalogQuery]:
    queries = []
    k = len(cycle)
    valuation = generate_valuations(1, get_cycle_vars(cycle))[0]
    head_content = q.get_key_vars(cycle[0]) + apply_valuation_to_atom_values(q.get_key_vars(cycle[0]), valuation)
    head = Atom("Link_" + str(rewriting_index), head_content)
    for i in range(0, k):
        query = DatalogQuery(head)
        for atom in cycle:
            query.add_atom(Atom("Keep_" + atom.name, atom.variables()))
            query.add_atom(Atom("Keep_" + atom.name, apply_valuation_to_atom_values(atom.variables(), valuation)))
        keys = q.get_key_vars(cycle[i])
        for var in keys:
            query.add_atom(EqualityAtom(var, valuation[var]))
        queries.append(query)
    return queries


def trans_queries(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) \
        -> Tuple[DatalogQuery, DatalogQuery, DatalogQuery]:
    valuations = generate_valuations(2, get_cycle_vars(cycle))
    sp1 = valuations[0]
    sp2 = valuations[1]

    x0 = q.get_key_vars(cycle[0])
    x0_sp1 = apply_valuation_to_atom_values(x0, sp1)
    x0_sp2 = apply_valuation_to_atom_values(x0, sp2)

    trans1_query = DatalogQuery(Atom("Trans_" + str(rewriting_index), x0 + x0_sp1))
    trans1_query.add_atom(Atom("Link", x0 + x0_sp1))

    trans2_query = DatalogQuery(Atom("Trans_" + str(rewriting_index), x0 + x0_sp1))
    trans3_query = DatalogQuery(Atom("Trans_" + str(rewriting_index), x0 + x0_sp2))

    trans2_query.add_atom(Atom("Trans_" + str(rewriting_index), x0 + x0_sp2))
    trans2_query.add_atom(Atom("Link_" + str(rewriting_index), x0_sp2 + x0_sp1))
    trans3_query.add_atom(Atom("Trans_" + str(rewriting_index), x0 + x0_sp1))
    trans3_query.add_atom(Atom("Link_" + str(rewriting_index), x0_sp2 + x0_sp1))

    return trans1_query, trans2_query, trans3_query


def id_queries(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> List[DatalogQuery]:
    queries = []
    key_vars = q.get_key_vars(cycle[0])
    valuations = generate_valuations(2, key_vars)
    val1_vars = apply_valuation_to_atom_values(key_vars, valuations[0])
    val2_vars = apply_valuation_to_atom_values(key_vars, valuations[1])
    for var in key_vars:
        lower_query = DatalogQuery(Atom("Lower_" + str(rewriting_index), key_vars + val1_vars))
        lower_query.add_atom(Atom("Trans_" + str(rewriting_index), key_vars + val1_vars))
        lower_query.add_atom(Atom("Trans_" + str(rewriting_index), key_vars + val2_vars))
        lower_query.add_atom(CompareAtom(valuations[0][var], valuations[1][var], True))
        queries.append(lower_query)

    id_query = DatalogQuery(Atom("IdentifiedBy_" + str(rewriting_index), key_vars + val1_vars))
    id_query.add_atom(Atom("Link_" + str(rewriting_index), key_vars + val2_vars))
    id_query.add_atom(Atom("Lower_" + str(rewriting_index), key_vars + val1_vars), True)
    queries.append(id_query)

    return queries


def t_query(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> DatalogQuery:
    variables = get_cycle_vars(cycle)
    valuation = generate_valuations(1, variables)[0]
    head_content = apply_valuation_to_atom_values(cycle[0].variables(), valuation) + variables
    query = DatalogQuery(Atom("T_" + str(rewriting_index), head_content))
    for atom in cycle:
        query.add_atom(Atom("Keep_" + atom.name, atom.variables()))
    key_vars = q.get_key_vars(cycle[0])
    valuated = apply_valuation_to_atom_values(key_vars, valuation)
    query.add_atom(Atom("IdentifiedBy_" + str(rewriting_index), key_vars + valuated))
    return query


def n_queries(cycle: List[Atom], q: ConjunctiveQuery, rewriting_index: int) -> List[DatalogQuery]:
    queries = []
    k = len(cycle)
    variables = get_cycle_vars(cycle)
    valuation = generate_valuations(1, variables)[0]
    key0_vars = q.get_key_vars(cycle[0])
    valuated = apply_valuation_to_atom_values(key0_vars, valuation)
    for i in range(0, k):
        query = DatalogQuery(Atom("N_" + cycle[i].name, q.get_key_vars(cycle[i]) + valuated))
        query.add_atom(Atom("T_" + str(rewriting_index), valuated + variables))
        queries.append(query)
    return queries

import networkx as nx
from data_structures import ConjunctiveQuery
from algorithms import gen_attack_graph, gen_m_graph, all_cycles_weak, find_bad_internal_fd, initial_strong_components
from rewriting_algorithms.fo_rewriting import rewrite_fo


def rewrite(q: ConjunctiveQuery):
    a_graph = gen_attack_graph(q)
    if all_cycles_weak(a_graph, q):
        bad = find_bad_internal_fd(q)
        if len(bad) != 0:
            # saturate q
            pass
        rewritten = []
        rewriting_index = 0;
        while len(a_graph.nodes) > 0:
            not_attacked_atoms = [atom for atom in a_graph.nodes if a_graph.in_degree(atom) == 0]
            if len(not_attacked_atoms) > 0:
                rewrite_fo(q, not_attacked_atoms[0], rewritten, rewriting_index)
                q.remove_atom(not_attacked_atoms[0])
                rewriting_index += 3
            else:
                m_graph = gen_m_graph(q.atoms)
                cycles = nx.simple_cycles(m_graph)
                isccs = initial_strong_components(a_graph)
                good_cycles = []
                for cycle in cycles:
                    for iscc in isccs:
                        if set(cycle).issubset(iscc):
                            good_cycles.append(cycle)
                # delete_weak_cycle(self, good_cycles[0], res)

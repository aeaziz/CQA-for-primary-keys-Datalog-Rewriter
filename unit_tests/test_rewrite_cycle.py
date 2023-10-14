from data_structures import AtomValue, Atom, DatalogQuery, ConjunctiveQuery, FunctionalDependency
from rewriting_algorithms.cycle_rewriting import rewrite_cycle


def test_pk_query():
    x = AtomValue("X", True)
    y = AtomValue("Y", True)
    z = AtomValue("Z", True)
    r = Atom("R", [x, y])
    s = Atom("S", [y, z])
    t = Atom("T", [z, x])
    q = ConjunctiveQuery({
        r: (frozenset([FunctionalDependency(frozenset([x]), y)]), [True, False], False),
        s: (frozenset([FunctionalDependency(frozenset([y]), z)]), [True, False], False),
        t: (frozenset([FunctionalDependency(frozenset([z]), x)]), [True, False], False)
    }, [])
    print(rewrite_cycle([r, s, t], q, 0))

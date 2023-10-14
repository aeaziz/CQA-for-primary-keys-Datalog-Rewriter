from data_structures import AtomValue, Atom, ConjunctiveQuery, FunctionalDependency
from algorithms import find_bad_internal_fd
from rewriting_algorithms.saturation import saturate


def test_saturation():
    x = AtomValue("X", True)
    y = AtomValue("Y", True)
    z = AtomValue("Z", True)
    r = Atom("R", [x, y])
    s = Atom("S", [x, z])
    t = Atom("T", [x, z])
    q = ConjunctiveQuery({
        r: (frozenset([FunctionalDependency(frozenset([x]), y)]), [True, False], False),
        s: (frozenset([FunctionalDependency(frozenset([x]), z)]), [True, False], False),
        t: (frozenset([FunctionalDependency(frozenset([x]), z)]), [True, False], False)
    }, [])
    bad = find_bad_internal_fd(q)
    assert bad == frozenset([FunctionalDependency(frozenset([x]), z)])
    saturate(q, find_bad_internal_fd(q))
    bad = find_bad_internal_fd(q)
    assert bad == frozenset()
    assert Atom("N_0", [x, z]) in q.content

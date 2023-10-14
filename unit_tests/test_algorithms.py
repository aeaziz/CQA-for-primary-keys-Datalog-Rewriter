import pytest
from data_structures import AtomValue, FunctionalDependency, Atom, ConjunctiveQuery, SequentialProof
from algorithms import transitive_closure, atom_plus, gen_attack_graph, all_cycles_weak, atom_attacks_variables, \
    gen_m_graph, sequential_proofs, fd_is_internal, find_bad_internal_fd


@pytest.fixture
def test1_vars():
    x = AtomValue("X", True)
    y = AtomValue("Y", True)
    z = AtomValue("Z", True)
    a = AtomValue("A", True)
    b = AtomValue("B", True)
    return x, y, z, a, b


@pytest.fixture
def test1_fds(test1_vars):
    x, y, z, a, b = test1_vars
    fd1 = FunctionalDependency(frozenset([x, y]), z)
    fd2 = FunctionalDependency(frozenset([a]), x)
    fd3 = FunctionalDependency(frozenset([b]), y)
    fd4 = FunctionalDependency(frozenset([a]), b)
    return fd1, fd2, fd3, fd4


@pytest.fixture
def test1_atoms(test1_vars, test1_fds):
    x, y, z, a, b = test1_vars
    r = Atom("R", [x, y, z])
    s = Atom("S", [a, x])
    t = Atom("T", [b, y])
    v = Atom("V", [a, b])
    return r, s, t, v


@pytest.fixture
def test1_query(test1_atoms, test1_fds):
    r, s, t, v = test1_atoms
    fd1, fd2, fd3, fd4 = test1_fds
    q = ConjunctiveQuery({
        r: (frozenset([fd1]), [True, True, False], False),
        s: (frozenset([fd2]), [True, False], False),
        t: (frozenset([fd3]), [True, False], False),
        v: (frozenset([fd4]), [True, False], False)}, [])
    return q


@pytest.fixture
def test2_fds(test1_vars):
    x, y, z, a, b = test1_vars
    fd1 = FunctionalDependency(frozenset([x]), y)
    fd2 = FunctionalDependency(frozenset([y]), z)
    fd3 = FunctionalDependency(frozenset([x]), b)
    fd4 = FunctionalDependency(frozenset([b]), z)
    fd5 = FunctionalDependency(frozenset([y]), a)
    fd6 = FunctionalDependency(frozenset([a]), z)
    return fd1, fd2, fd3, fd4, fd5, fd6


@pytest.fixture
def test2_atoms(test1_vars):
    x, y, z, a, b = test1_vars
    s1 = Atom("S1", [x, y])
    s2 = Atom("S2", [y, z])
    r1 = Atom("R1", [x, b])
    r2 = Atom("R2", [b, z])
    t1 = Atom("T1", [y, a])
    t2 = Atom("T2", [a, z])
    return s1, s2, r1, r2, t1, t2


@pytest.fixture
def test2_query(test2_fds, test2_atoms):
    # S1(X, Y), S2(Y, Z), R1(X, B), R2(B, Z),T1(Y, A), T2(A, Z)
    fd1, fd2, fd3, fd4, fd5, fd6 = test2_fds
    s1, s2, r1, r2, t1, t2 = test2_atoms
    q = ConjunctiveQuery({
        s1: (frozenset([fd1]), [True, False], False),
        s2: (frozenset([fd2]), [True, False], False),
        r1: (frozenset([fd3]), [True, False], False),
        r2: (frozenset([fd4]), [True, False], False),
        t1: (frozenset([fd5]), [True, False], False),
        t2: (frozenset([fd6]), [True, False], False)
    }, [])
    return q


def test_transitive_closure(test1_vars, test1_fds):
    x, y, z, a, b, = test1_vars
    fd_set = set(test1_fds)
    assert transitive_closure(set([a]), fd_set) == set([x, y, z, a, b])
    assert transitive_closure(set([b]), fd_set) == set([b, y])
    assert transitive_closure(set([x]), fd_set) == set([x])
    assert transitive_closure(set([x, y]), fd_set) == set([x, y, z])


def test_plus(test1_vars, test1_atoms, test1_query):
    q = test1_query
    x, y, z, a, b = test1_vars
    r, s, t, v = test1_atoms
    assert atom_plus(r, q) == set([x, y])
    assert atom_plus(s, q) == set([a, b, y])
    assert atom_plus(t, q) == set([b])
    assert atom_plus(v, q) == set([a, x])


def test_a_graph(test1_atoms, test1_query):
    q = test1_query
    r, s, t, v = test1_atoms
    a_graph = gen_attack_graph(q)
    edges = [(s, r), (t, r), (t, s), (t, v), (v, r), (v, t)]
    for e in a_graph.edges:
        assert e in edges
    for e in edges:
        assert e in a_graph.edges


def test_m_graph(test1_atoms, test1_query):
    q = test1_query
    r, s, t, v = test1_atoms
    m_graph = gen_m_graph(q)
    edges = [(v, t), (v, s), (s, v)]
    for e in m_graph.edges:
        assert e in edges
    for e in edges:
        assert e in m_graph.edges


def test_weak_cycle(test1_vars, test1_fds, test1_atoms, test1_query):
    x, y, z, a, b = test1_vars
    fd1, fd2, fd3, fd4 = test1_fds
    r, s, t, v = test1_atoms
    q = test1_query
    a_graph1 = gen_attack_graph(q)
    n = [FunctionalDependency(frozenset([x]), a)]
    supp_r = Atom("R", [x, a])
    q2 = ConjunctiveQuery({
        s: (frozenset([fd2]), [True, False], False),
        supp_r: (frozenset(n), [True, False], False)
    }, [])
    a_graph2 = gen_attack_graph(q2)
    q3 = ConjunctiveQuery({
        r: (frozenset([fd1]), [True, True, False], False),
        s: (frozenset([fd2]), [True, False], False)
    }, [])
    a_graph3 = gen_attack_graph(q3)

    assert all_cycles_weak(a_graph1, q) is False
    assert all_cycles_weak(a_graph2, q2) is True
    assert all_cycles_weak(a_graph3, q3) is True


def test_attack_variable(test1_vars, test1_atoms, test1_query):
    x, y, z, a, b = test1_vars
    r, s, t, v = test1_atoms
    q = test1_query
    assert atom_attacks_variables(s, x, q) is True
    assert atom_attacks_variables(v, x, q) is False
    assert atom_attacks_variables(t, x, q) is True
    assert atom_attacks_variables(r, x, q) is False


def test_sequential_proof(test1_vars, test1_atoms, test1_query):
    x, y, z, a, b = test1_vars
    r, s, t, v = test1_atoms
    q = test1_query
    fd = FunctionalDependency(frozenset([a]), z)
    sps = sequential_proofs(fd, q)
    expected_sps = [SequentialProof(fd, [s, t, v, r])]
    assert sps == expected_sps


def test_is_internal(test1_vars, test2_fds, test2_atoms, test2_query):
    x, y, z, a, b = test1_vars
    fd1, fd2, fd3, fd4, fd5, fd6 = test2_fds
    q = test2_query
    fd = FunctionalDependency(frozenset([x]), z)
    assert fd_is_internal(fd1, q) is False
    assert fd_is_internal(fd, q) is True


def test_is_saturated(test2_atoms, test2_query):
    s1, s2, r1, r2, t1, t2 = test2_atoms
    q = test2_query

    assert len(find_bad_internal_fd(q)) > 0
    q.content[s1] = (q.content[s1][0], q.content[s1][1], True)
    q.content[s2] = (q.content[s2][0], q.content[s2][1], True)
    assert len(find_bad_internal_fd(q)) == 0

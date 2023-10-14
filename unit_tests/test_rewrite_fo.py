import pytest

from data_structures import AtomValue, Atom, ConjunctiveQuery, FunctionalDependency, EqualityAtom, DatalogQuery
from rewriting_algorithms.fo_rewriting import rewrite_fo
from file_handle import read_cq_file, read_datalog_file


@pytest.fixture
def test_simple_vars():
    x = AtomValue("X", True)
    y = AtomValue("Y", True)
    z = AtomValue("Z", True)
    return x, y, z


@pytest.fixture
def test_simple_fds(test_simple_vars):
    x, y, z = test_simple_vars
    fd1 = FunctionalDependency(frozenset([x]), y)
    fd2 = FunctionalDependency(frozenset([y]), z)
    return fd1, fd2


@pytest.fixture
def test_simple_atoms(test_simple_vars):
    x, y, z = test_simple_vars
    r = Atom("R", [x, y])
    s = Atom("S", [y, z])
    return r, s


@pytest.fixture
def test_simple_query(test_simple_atoms, test_simple_fds):
    """r, s = test_simple_atoms
    fd1, fd2 = test_simple_fds
    q = ConjunctiveQuery({
        r: (frozenset([fd1]), [True, False], False),
        s: (frozenset([fd2]), [True, False], False)
    }, [])
    return q"""
    return read_cq_file("test_files/CQ/fo_sample1.txt")[0]


@pytest.fixture
def test_simple_solution(test_simple_vars, test_simple_atoms):
    x, y, z = test_simple_vars
    z0 = AtomValue("Z_0", True)
    r, s = test_simple_atoms
    r0_head = Atom("R_0", [])
    r1_head = Atom("R_1", [x])
    r2_head = Atom("R_2", [x, y])
    r0 = DatalogQuery(r0_head)
    r0.add_atom(r)
    r0.add_atom(r1_head, True)
    r1 = DatalogQuery(r1_head)
    r1.add_atom(Atom("R", [x, z0]))
    r1.add_atom(Atom("R_2", [x, z0]), True)
    r2 = DatalogQuery(r2_head)
    r2.add_atom(r)
    r2.add_atom(s)
    return [r0, r1, r2]


@pytest.fixture
def test_constant_vars(test_simple_vars):
    x, y, z = test_simple_vars
    a = AtomValue("a", False)
    b = AtomValue("b", False)
    return x, y, z, a, b


@pytest.fixture
def test_constant_atoms(test_constant_vars):
    x, y, z, a, b = test_constant_vars
    r = Atom("R", [x, y, a])
    s = Atom("S", [y, b, z])
    return r, s


@pytest.fixture
def test_constant_query(test_constant_atoms, test_simple_fds):
    r, s = test_constant_atoms
    fd1, fd2 = test_simple_fds
    q = ConjunctiveQuery({
        r: (frozenset([fd1]), [True, False, False], False),
        s: (frozenset([fd2]), [True, False, False], False)
    }, [])
    return q


@pytest.fixture
def test_constant_solution(test_constant_vars, test_constant_atoms):
    x, y, z, a, b = test_constant_vars
    z0 = AtomValue("Z_0", True)
    z1 = AtomValue("Z_1", True)
    r, s = test_constant_atoms
    r0_head = Atom("R_0", [])
    r1_head = Atom("R_1", [x])
    r2_head = Atom("R_2", [x, y, z1])
    r3_head = Atom("R_3", [x, y])
    r4_head = Atom("R_4", [x, y])
    r5_head = Atom("R_5", [x, y, z0, z])
    r0 = DatalogQuery(r0_head)
    r0.add_atom(r)
    r0.add_atom(r1_head, True)
    r1 = DatalogQuery(r1_head)
    r1.add_atom(Atom("R", [x, z0, z1]))
    r1.add_atom(Atom("R_2", [x, z0, z1]), True)
    r2 = DatalogQuery(r2_head)
    r2.add_atom(Atom("R", [x, y, z1]))
    r2.add_atom(EqualityAtom(z1, a))
    r2.add_atom(r3_head)
    r3 = DatalogQuery(r3_head)
    r3.add_atom(r)
    r3.add_atom(s)
    r3.add_atom(r4_head, True)
    r4 = DatalogQuery(r4_head)
    r4.add_atom(r)
    r4.add_atom(Atom("S", [y, z0, z1]))
    r4.add_atom(Atom("R_5", [x, y, z0, z1]), True)
    r5 = DatalogQuery(r5_head)
    r5.add_atom(r)
    r5.add_atom(Atom("S", [y, z0, z]))
    r5.add_atom(EqualityAtom(z0, b))
    return [r0, r1, r2, r3, r4, r5]


@pytest.fixture
def test_multiple_atoms(test_simple_vars):
    x, y, z = test_simple_vars
    r = Atom("R", [x, y, x])
    s = Atom("S", [y, z])
    return r, s


@pytest.fixture
def test_multiple_query(test_multiple_atoms, test_simple_fds):
    r, s = test_multiple_atoms
    fd1, fd2 = test_simple_fds
    q = ConjunctiveQuery({
        r: (frozenset([fd1]), [True, False, False], False),
        s: (frozenset([fd2]), [True, False], False)
    }, [])
    return q


@pytest.fixture
def test_multiple_solution(test_multiple_atoms, test_simple_vars):
    x, y, z = test_simple_vars
    z0 = AtomValue("Z_0", True)
    z1 = AtomValue("Z_1", True)
    r, s = test_multiple_atoms
    r0_head = Atom("R_0", [])
    r1_head = Atom("R_1", [x])
    r2_head = Atom("R_2", [x, y, z1])
    r3_head = Atom("R_3", [x, y])
    r0 = DatalogQuery(r0_head)
    r0.add_atom(r)
    r0.add_atom(r1_head, True)
    r1 = DatalogQuery(r1_head)
    r1.add_atom(Atom("R", [x, z0, z1]))
    r1.add_atom(Atom("R_2", [x, z0, z1]), True)
    r2 = DatalogQuery(r2_head)
    r2.add_atom(Atom("R", [x, y, z1]))
    r2.add_atom(EqualityAtom(z1, x))
    r2.add_atom(r3_head)
    r3 = DatalogQuery(r3_head)
    r3.add_atom(r)
    r3.add_atom(s)
    return [r0, r1, r2, r3]


def compare_with_solution(result, solution):
    assert len(solution) == len(result)
    for i in range(len(solution)):
        print(result[i])
        assert solution[i] == result[i]


def generate_result(atoms_order, query):
    atoms_done = set()
    queries_res = []
    for atom in atoms_order:
        queries_res = queries_res + rewrite_fo(query, atom, atoms_done, len(queries_res))
        atoms_done.add(atom)
    return queries_res


def test_simple(test_simple_query, test_simple_atoms, test_simple_solution):
    compare_with_solution(generate_result(test_simple_atoms, test_simple_query), test_simple_solution)


def test_constant(test_constant_query, test_constant_atoms, test_constant_solution):
    compare_with_solution(generate_result(test_constant_atoms, test_constant_query), test_constant_solution)


def test_multiple(test_multiple_query, test_multiple_atoms, test_multiple_solution):
    compare_with_solution(generate_result(test_multiple_atoms, test_multiple_query), test_multiple_solution)

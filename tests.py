from a_graph import AttackGraph
from m_graph import MGraph
from f_graph import FGraph
from saturator import Saturator

# Test to see if the query has been parsed correctly
def show_infos(t, p):
    print("\n\n\n")
    print("Query : ")
    print(p.string)
    print("\n")
    print("Atoms : ")
    print(t.body)
    print("\n")
    print("Functional dependencies : ")
    print(t.fd)


# Test to see if the attack graphs are generated correctly
def test_a_graph(t):
    print("\n\n\n")
    a = AttackGraph(t)
    print("ATTACK GRAPH")
    print("\n")
    print("Nodes : ")
    print(a.vertex)
    print("\n")
    for vertex in a.edges:
        for n in a.edges[vertex]:
            print(str(vertex) + " attacks " + str(n))

    print("\n\n\n")
    print("Does q contain only weak cycles? : " + str(a.all_cycles_weak()))


# Test to see of the M Graph are generated correctly
def test_m_graph(t):
    print("\n\n\n")
    print("M-GRAPH")
    m = MGraph(t)
    print("\n")
    print("Nodes : ")
    print(m.vertex)
    print("\n")
    for vertex in m.edges:
        for n in m.edges[vertex]:
            print(str(vertex) + " --M--> " + str(n))


# Test to see if the F Graph are generated correctly
def test_f_graph(t):
    f = FGraph(t)
    print("\n\n\n")
    print("F-GRAPH")
    print("\n")
    print("Nodes : ")
    print(f.vertex)
    print("\n")
    print("EDGES : ")
    for v in f.edges:
        for x in f.edges[v]:
            if str(x) != str(v):
                print(str(v) + " --" + str(f.label[v][x]) + "--> " + str(x))


# Test to see if the saturation test and the saturation process works correctly
def test_saturate(t):
    f = FGraph(t)
    print("\n")
    print("SEQUENTIAL PROOFS")
    for (v1, v2, p) in f.find_sequential_proofs():
        print(str(p) + " for " + str(v1) + " --> " + str(v2))

    print("\n")
    print("INTERNAL FD")
    for fd in t.fd.find_internal_fd():
        print(fd)

    print("\n")
    print("IS SATURATED? : " + str(t.is_saturated()))

    print("\n")

    sat = Saturator(t)
    res = sat.saturate()
    for q in res:
        print(q)
    print("\n")
    print(t.body)


# Test to see if the translation works correctly
def test_translate(t):
    print("\n\n\n")
    datalog_program = t.translate()
    f = open("output.txt", "w+")
    for q in datalog_program:
        if str(q)[0] == "%":
            f.write("\n\n")
        f.write(str(q)+"\n")
    print("DONE")
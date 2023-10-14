import regex
from data_structures import ConjunctiveQuery, DatalogQuery, Atom, AtomValue, EqualityAtom, CompareAtom, \
    FunctionalDependency
from typing import List, FrozenSet


def read_datalog_file(file: str) -> List[DatalogQuery]:
    f = open(file, "r")

    names_regex = "[A-Za-z][A-Za-z0-9_]*"
    atom_regex = names_regex + "\(" + "(" + names_regex + ",)*" + names_regex + "\)"
    other_regex = names_regex + "(=|!=|>|<)" + names_regex
    query_element_regex = "(" + other_regex + "|" + "(not )?" + atom_regex + ")"
    query_regex = "^" + atom_regex + " :- " + "(" + query_element_regex + ", )*" + query_element_regex + "\.$"
    queries = []
    for line in f:
        if regex.match(query_regex, line):
            elements = regex.findall(query_element_regex, line)
            head = parse_atom(elements[0][0])
            q = DatalogQuery(head)
            for element in elements[1:]:
                atom_element = element[0]
                if "not" in atom_element:
                    q.add_atom(parse_atom(atom_element[3:]), True)
                elif "=" in atom_element:
                    q.add_atom(parse_equality_atom(atom_element))
                elif ">" in atom_element or "<" in atom_element:
                    q.add_atom(parse_compare_atom(atom_element))
                else:
                    q.add_atom(parse_atom(atom_element))
            queries.append(q)
        else:
            print("NOT OK")
    return queries


def read_cq_file(file: str) -> List[DatalogQuery]:
    f = open(file, "r")
    names_regex = "[A-Za-z][A-Za-z0-9_]*"
    atom_regex = names_regex + "\(" + "\[(?>" + names_regex + ",)*" + names_regex + "\](?>," + names_regex + ")*\)\*?"
    query_regex = "^(?>" + atom_regex + ",)*"+atom_regex+"$"
    queries = []
    for line in f:
        if regex.match(query_regex, line):
            elements = regex.findall(atom_regex, line)
            q = ConjunctiveQuery({}, [])
            for element in elements:
                atom_element = element
                consistent = False
                if "*" in atom_element:
                    consistent = True
                    atom_element = atom_element[:-1]
                key_length = len(atom_element.split("[")[1].split("]")[0].split(","))
                atom = parse_atom(atom_element.replace("[", "").replace("]", ""))
                fds = parse_fds(key_length, atom)
                is_key = [True for i in range(key_length)] + [False for i in range(len(atom.content) - key_length)]
                q.add_atom(atom, fds, is_key, consistent)
            queries.append(q)
        else:
            print("NOT OK")
    return queries


def parse_atom(atom: str) -> Atom:
    name, body = atom.split("(")
    body = body[:-1]
    values = [parse_atom_value(atom_value) for atom_value in body.split(",")]
    return Atom(name, values)


def parse_equality_atom(atom: str) -> EqualityAtom:
    if "!=" in atom:
        v1, v2 = atom.split("!=")
        return EqualityAtom(parse_atom_value(v1), parse_atom_value(v2), True)
    else:
        v1, v2 = atom.split("=")
        return EqualityAtom(parse_atom_value(v1), parse_atom_value(v2))


def parse_compare_atom(atom: str) -> CompareAtom:
    if ">" in atom:
        v1, v2 = atom.split(">")
        return CompareAtom(parse_atom_value(v1), parse_atom_value(v2), True)
    else:
        v1, v2 = atom.split("<")
        return CompareAtom(parse_atom_value(v1), parse_atom_value(v2), False)


def parse_atom_value(atom_value: str) -> AtomValue:
    return AtomValue(atom_value, atom_value[0].isupper())


def parse_fds(key_length: int, atom: Atom) -> FrozenSet[FunctionalDependency]:
    key = []
    fds = []
    for i in range(key_length):
        if atom.content[i].var:
            key.append(atom.content[i])
    for var in atom.variables():
        if var not in key:
            fds.append(FunctionalDependency(frozenset(key), var))
    return frozenset(fds)

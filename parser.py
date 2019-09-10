import os
import re
from translate import TranslateInput
from datalog import Atom
from functional_dependencies import FD


# Class that parses a file into a TranslateInput Object
class Parser:
    def __init__(self, file):
        if os.path.isfile(file):
            with open(file, 'r') as content_file:
                self.string = content_file.read().replace(" ","")
                if not self.is_well_formed():
                    raise NotAQuery
                else:
                    self.t = TranslateInput()

        else:
            raise FileNotFound

    # True if the file respects the specified format
    def is_well_formed(self):
        atom_pattern = "[A-Z]+[A-Z0-9_]*\(\[[A-Za-z0-9]+(,[A-Za-z0-9_]+)*\](,[A-Za-z0-9_]+)*\)"
        pattern = re.compile("^(" + atom_pattern + ")+(," + atom_pattern + ")*$")
        return pattern.match(self.string)

    # Parses the file, returning a TranslateInput Object
    def parse(self):
        atoms = re.findall("[A-Z]+[A-Za-z0-9_]*\(.*?\)", self.string)
        for a in atoms:
            self.parse_atom(a)
        self.t.generate_fd_set()
        self.t.generate_attack_graph()
        self.t.generate_f_graph()
        return self.t

    # Parses an atom
    def parse_atom(self, atom_string):
        name, body = atom_string.split("(")
        atom = Atom(name)
        key_values = body[1:-1].split("]")[0]
        key_var = re.findall("[A-Z]+[A-Z_0-9]*", key_values)
        other_values = body[1:-1].split("]")[1]
        other_var = re.findall("[A-Z]+[A-Z_0-9]*", other_values)
        for value in key_values.split(","):
            if value in key_var:
                atom.add_variable(value, True)
            else:
                atom.add_constant(value, True)
        for value in other_values[1:].split(","):
            if value in other_var:
                atom.add_variable(value, False)
            else:
                atom.add_constant(value, False)
        self.t.body.add_atom(atom)
        return atom


# Exception used for non-existing files
class FileNotFound(Exception):
    pass


# Exception used for malformed files
class NotAQuery(Exception):
    pass

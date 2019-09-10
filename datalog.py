# Represents an atom
class Atom:
    def __init__(self, name):
        self.name = name
        self.content = []
        self.is_key = []
        self.is_variable = []
        self.consistent = False
        self.negative = False

    # Returns the variables appearing in this atom
    def get_variables(self):
        res = []
        for i in range(0, len(self.content)):
            if self.is_variable[i]:
                res.append(self.content[i])
        return res

    # Returns the constants appearing in this atom
    def get_constants(self):
        res = []
        for i in range(0, len(self.content)):
            if not self.is_variable[i]:
                res.append(self.content[i])
        return res

    # Adds a variable
    def add_variable(self, value, is_key):
        self.content.append(value)
        self.is_variable.append(True)
        self.is_key.append(is_key)

    # Adds a constant
    def add_constant(self, value, is_key):
        self.content.append(value)
        self.is_variable.append(False)
        self.is_key.append(is_key)

    # The variable becomes a constant
    def freeze_variable(self, f):
        for var in self.content:
            if var == f:
                self.is_variable[self.content.index(var)] = False

    # Sets if the relation is consistent or not
    def set_consistent(self, value):
        self.consistent = value

    # Creates a copy of this atom
    def copy(self):
        new = Atom(self.name)
        new.content = self.content[:]
        new.is_key = self.is_key[:]
        new.is_variable = self.is_variable[:]
        new.consistent = self.consistent
        new.negative = self.negative
        return new

    # Returns the key-values of this atom
    def get_key_values(self):
        key_values = []
        for i in range(0, len(self.content)):
            if self.is_key[i]:
                key_values.append(self.content[i])
        return key_values

    # Returns the key-variables of this atom
    def get_key_variables(self):
        key_variables = []
        for i in range(0, len(self.content)):
            if self.is_key[i] and self.is_variable[i]:
                key_variables.append(self.content[i])
        return key_variables

    # Returns the values of this atom that doesn't appear in the key
    def get_not_key_values(self):
        not_key_values = []
        for i in range(0, len(self.content)):
            if not self.is_key[i]:
                not_key_values.append(self.content[i])
        return not_key_values

    # String representation when this atom is used as a Datalog Query head
    def str_as_head(self):
        prev = self.negative
        self.negative = False
        res = self.__str__()
        self.negative = prev
        return res

    def __eq__(self, other):
        return self.content == other.content and self.name == other.name

    def __str__(self):
        prefix = ""
        if self.negative:
            prefix = "not "

        if len(self.content) == 0:
            return prefix + self.name
        res = self.name + '('
        for c in self.content:
            res = res + c + ", "
        return prefix + res[:-2] + ")"

    def __repr__(self):
        return self.__str__()


# Represents an equality or inequality atom
class EqualityAtom:
    def __init__(self, left, right, inequality=False):
        self.left = left
        self.right = right
        self.inequality = inequality

    def __str__(self):
        if self.inequality:
            sign = "!="
        else:
            sign = "="
        return self.left + sign + self.right

    def __repr__(self):
        return self.__str__()


# Represents the min atom used in Datalog
class MinAtom:
    def __init__(self, var1, atom, var2):
        self.atom = atom
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return "#min{" + self.var1 + " : " + str(self.atom) + "} = " + self.var2

    def __repr__(self):
        return self.__str__()


# Represents the body of a datalog query
class DatalogBody:
    def __init__(self):
        self.atoms = []
        self.variables = set()
        self.constants = set()

    # Adds an atom
    def add_atom(self, atom):
        self.atoms.append(atom)
        if type(atom) == "Atom":
            self.variables = self.variables.union(set(atom.get_variables()))
            self.constants = self.constants.union(set(atom.get_constants()))

    # Rebuilds the set of variables and constants
    def rebuild_sets(self):
        self.variables = set()
        self.constants = set()
        for atom in self.atoms:
            self.variables = self.variables.union(set(atom.get_variables()))
            self.constants = self.constants.union(set(atom.get_constants()))

    # Removes an atom
    def remove_atom(self, atom):
        self.atoms.remove(atom)
        self.rebuild_sets()

    # Returns a copy of this body
    def copy(self):
        new = DatalogBody()
        new.atoms = self.atoms.copy()
        return new

    # Retrieves an atom using his name
    def get_atom(self, name):
        for atom in self.atoms:
            if atom.name == name:
                return atom

    # The variable becomes a constant
    def freeze_variable(self, var):
        if var in self.variables:
            self.variables.remove(var)
            self.constants.add(var)
            for atom in self.atoms:
                atom.freeze_variable(var)

    def __str__(self):
        return str(self.atoms).replace("[", "").replace("]", "")

    def __repr__(self):
        return self.__str__()


# Represents a datalog query
class DatalogQuery:
    def __init__(self, name):
        self.head = name
        self.body = DatalogBody()

    # Adds an atom to the body of the query
    def add_atom(self, atom):
        self.body.add_atom(atom)

    def __str__(self):
        return self.head.str_as_head() + " :- " + self.body.__str__() + "."

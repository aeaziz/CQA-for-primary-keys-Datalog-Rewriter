from parser import Parser
from tests import *

print("The following script generates a Datalog program (if possible) from a file containing a boolean sjfBCQ query")
print("\n")
print("An element between in lowercase is considered a constant, uppercase values will be considered as a variable")
print("\n")
print("Please surround the primary keys with brackets ('[]')")
print("\n")
print("Please don't use prefixes used in the generated Datalog program in your query (T, DCon, Pk, InLongDCycle, ...)")
print("\n")
print("Example : R([X,W],Y),S([Y],X)")

try:
    example = int(input("Please enter the example number : "))
    query_file = "./examples/query/example" + str(example) + ".txt"
    parser = Parser(query_file)
    t = parser.parse()
    datalog_program = t.translate()
    f = open("output.txt", "w+")
    for q in datalog_program:
        if str(q)[0] == "%":
            f.write("\n\n")
        f.write(str(q) + "\n")
except FileNotFound:
    print("The given file cannot be found")
except NotAQuery:
    print("The given does not respect the specified format")

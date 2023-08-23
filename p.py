import rdflib
from rdflib.plugins.parsers.notation3 import BadSyntax

def validate_ttl_syntax(filename):
    g = rdflib.Graph()
    try:
        g.parse(filename, format='turtle')
        print("The .ttl file has valid Turtle syntax!")
    except BadSyntax as e:
        print(f"Syntax error in the .ttl file: {e}")

filename = 'output_books.ttl'
validate_ttl_syntax(filename)

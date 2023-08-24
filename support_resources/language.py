from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

g = Graph()

# Parsing the .ttl file
g.parse("./merged_output.ttl", format="turtle")

ns1 = Namespace("http://schema.org/")

for s, p, o in g.triples((None, RDF.type, ns1.Book)):
    # Check if the book already has an inLanguage attribute
    language = g.value(s, ns1.inLanguage)
    if not language:
        # If not, add the inLanguage attribute with value 'Francais'
        g.add((s, ns1.inLanguage, Literal("Francais")))

# Serialize the graph into a new .ttl file
g.serialize(destination='_output.ttl', format='turtle')

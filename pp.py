from rdflib import Graph, Namespace, Literal

# Load the ttl file into an RDF graph
g = Graph()
g.parse("output_bnf.ttl", format="turtle")

# Define the required namespaces
ns1 = Namespace("http://schema.org/")

# Find books with empty author and remove them
for book, _, _ in g.triples((None, ns1.author, Literal(""))):
    g.remove((book, ns1.author, Literal("")))

# Save the modified RDF graph
g.serialize(destination="output_bnf.ttl", format="turtle")

import utils
from rdflib import Graph, Literal, URIRef, Namespace, BNode, RDF

ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.org/pbs/")

g = Graph()
g.parse("output_alignment.ttl", format="turtle")
for alignment in g.subjects(RDF.type, pbs.Alignment):
    a = utils.extract_data_alignment(g, alignment)
    print(a)

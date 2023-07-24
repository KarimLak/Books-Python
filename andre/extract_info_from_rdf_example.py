from rdflib import Graph, Literal, BNode
from rdflib.namespace import RDF, FOAF, XSD
import rdflib.namespace

# read ttl files of constellation
#------------------------------------------------------------------

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


# load the graph
g = Graph()
g.parse("output_constellation_updated_light.ttl", format="turtle")

# create a graph for processed books
processed_graph = Graph()

count_constellation = 0
for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.name))
    book_author = str(g.value(book, ns1.author))
    age_range =  list(g.objects(book, ns1.ageRange))
    count_constellation +=1
    continue

print("count_constellation", count_constellation)

### mettre tout sur meme graph ?
#------------------------------------------------------------------
# read ttl file of bnf

g = Graph()
g.parse("output_bnf_1_light.ttl", format="turtle")

# create a graph for processed books
processed_graph = Graph()

count_bnf = 0
for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.title))
    book_author = str(g.value(book, ns1.author))
    age_range =  str(g.value(book, ns1.publicDestinataire))
    count_bnf += 1
    continue

print("count_bnf", count_bnf)

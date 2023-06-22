from rdflib import Graph, Namespace

# Define your namespaces
ns1 = Namespace("http://schema.org/")

# Load your graph
books = Graph()
books.parse("./books.ttl", format="ttl")

# Iterate over the books and print the book URI if it has the certain award
award_to_search = "aires du Québec : BD"
for s, p, o in books.triples((None, ns1.award, None)):
    if award_to_search in str(o):
        print(str(s))

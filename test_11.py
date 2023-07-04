from rdflib import RDF, Graph, Namespace
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Load the graphs
g_missing = Graph()
g_updated = Graph()

g_missing.parse("missing_outputs.ttl", format="turtle", encoding='utf-8')
g_updated.parse("books_updated.ttl", format="turtle", encoding='utf-8')

# Define the namespaces and predicates you're using
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.com/pbs#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

g_updated.bind("ns1", ns1)
g_updated.bind("pbs", pbs)
g_updated.bind("rdfs", rdfs)

title_pred = ns1["name"]  # replace with actual title predicate

# Iterate over the books in missing_output.ttl
for book1 in g_missing.subjects(RDF.type, ns1.Book):
    title1 = str(g_missing.value(book1, title_pred))

    # Compare this book's title with titles of books in updated_books.ttl
    for book2 in g_updated.subjects(RDF.type, ns1.Book):
        title2 = str(g_updated.value(book2, title_pred))

        # If the titles are similar, print the URI of the book in missing_output.ttl
        if similar(title1, title2) > 0.95 and title1.strip() != "":  # adjust the threshold as needed
            print(title1.strip() + " : " + title2.strip())

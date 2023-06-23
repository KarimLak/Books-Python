from rdflib import Graph, Namespace, URIRef

# Define your namespaces
ns1 = Namespace("http://schema.org/")
mcc = Namespace("http://example.com/mcc#")  

# Load your graphs
books = Graph()
awards = Graph()

books.parse("./books.ttl", format="turtle")
awards.parse("./awards.ttl", format="turtle")

# Collect all book URIs in the books graph
book_uris = set(str(s) for s, p, o in books if isinstance(s, URIRef) and str(s).startswith(ns1))

# Check if each book URI is present in the awards graph
for book_uri in book_uris:
    book_uri = URIRef(book_uri.replace(str(ns1), str(ns1)))
    if (None, mcc["R37"], book_uri) not in awards:
        print(f"The book {book_uri} is not present in the awards graph.")

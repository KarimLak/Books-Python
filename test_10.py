from rdflib import Graph, RDF, Namespace

# Define your namespaces
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.com/pbs#")
mcc = Namespace("http://example.com/mcc#")
schema = Namespace("http://schema.org/")

# Create a new graph and parse in an existing ttl files
g_missing_outputs = Graph()
g_missing_outputs.parse("./missing_outputs.ttl", format="turtle")

g_awards = Graph()
g_awards.parse("./awards.ttl", format="turtle")

# Loop over all books in the missing_outputs graph
for book in g_missing_outputs.subjects(RDF.type, ns1.Book):
    # Extract the book ID from the book URI
    book_id = book.split('/')[-1]

    # Formulate the book reference as it should appear in the awards.ttl file
    book_reference = schema[book_id]

    # If the book_reference is not found in the awards graph
    if not any(book_reference in objects for s, p, objects in g_awards):
        print(book)

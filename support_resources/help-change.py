from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

# Namespaces
ns1 = Namespace("http://schema.org/")

# Load the books graph
books_g = Graph()
books_g.parse("./final_output_merged_final.ttl", format="turtle", encoding="utf-8")

# Check for multiple dateReceived
for s in books_g.subjects(RDF.type, ns1.Book):
    # Get the book's information
    book_name = str(books_g.value(s, ns1.name))
    date_received = list(books_g.objects(s, ns1.dateReceived))

    if len(date_received) > 1:
        print(f"Book '{book_name}' has multiple dateReceived attributes.")

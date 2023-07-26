from rdflib import Graph, URIRef

# Load the .ttl files into RDF graphs
g = Graph()
g.parse("output_bnf_2.ttl", format="turtle")

g_updated = Graph()
g_updated.parse("output_bnf_2_updated.ttl", format="turtle")

# Create a set of subjects from the updated graph
updated_books = set(g_updated.subjects())

# Iterate over all the subjects in the original graph
for book in g.subjects():
    # Check if the book is not already in the updated graph
    if book not in updated_books:
        # If not, copy all the triples related to this book to the updated graph
        for pred, obj in g.predicate_objects(book):
            g_updated.add((book, pred, obj))

# Save the updated graph
g_updated.serialize("output_bnf_2_updated.ttl", format="turtle")


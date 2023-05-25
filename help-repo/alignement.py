from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
import os

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# List of input file paths
input_files = [
    "./output_bookcentre.ttl",
    "./output_fmdoc.ttl",
    "./output_lurelu.ttl",
    "./output_prixdeslibraires_bd.ttl",
    "./output_prixdeslibraires_essai.ttl",
    "./output_prixdeslibraires_jeunesse.ttl",
    "./output_prixdeslibraires_poesie.ttl",
    "./output_prixdeslibraires_roman.ttl",
    "./output_ricochet.ttl",
]

# Create a new graph
g = Graph()

# Load all files into the graph
for file in input_files:
    if os.path.exists(file):
        g.parse(file, format="ttl")

# A dictionary to store the books
books = {}

# Iterate over all books in the graph
for book in g.subjects(RDF.type, ns1.Book):
    # Get the name and author of the book
    name = g.value(book, ns1.name)
    author = g.value(book, ns1.author)

    # Use the name and author as a key in the dictionary
    key = (name, author)
    if key not in books:
        # If this is the first book with this name and author, add it to the dictionary
        books[key] = book
    else:
        # If there is already a book with this name and author, merge the two books
        for p, o in g.predicate_objects(book):
            # Add all triples from the current book to the first book with this name and author
            g.add((books[key], p, o))

        # Remove the current book from the graph
        g.remove((book, None, None))

# Save the merged graph
g.serialize(destination='merged_output.ttl', format='turtle')

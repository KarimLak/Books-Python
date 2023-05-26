from rdflib import Graph, Namespace, RDF
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

# Custom hash function for a dictionary with set values
def hash_dict(d):
    return hash(frozenset((k, frozenset(v)) for k, v in d.items()))

# A dictionary to store the books, using the custom hash function
books = {}

# Counter for merged books
merged_books = 0

# Iterate over all books in the graph
for book in g.subjects(RDF.type, ns1.Book):
    # Get all attributes of the book
    attributes = {attr: set(g.objects(book, attr)) for attr in g.predicates(book)}

    # Ignore 'url' and 'award' attributes
    attributes.pop(ns1.url, None)
    attributes.pop(ns1.award, None)

    # Use the attributes as a key in the dictionary
    key = hash_dict(attributes)
    if key not in books:
        # If this is the first book with these attributes, add it to the dictionary
        books[key] = (book, attributes)
    else:
        # If there is already a book with these attributes, merge the two books
        existing_book, existing_attributes = books[key]
        for p, o in g.predicate_objects(book):
            # Add the attribute to the first book if it's not already present
            if o not in existing_attributes.get(p, []):
                g.add((existing_book, p, o))

        # Remove the current book from the graph
        g.remove((book, None, None))

        # Increment the merged books counter
        merged_books += 1

print(f'Merged {merged_books} books.')

# Save the merged graph
g.serialize(destination='merged_output.ttl', format='turtle')

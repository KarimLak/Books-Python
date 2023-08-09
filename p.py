import rdflib
from difflib import get_close_matches
import re

# Normalization function for book names
def normalize_name(name):
    name = re.sub(r'[^a-z0-9\s]', '', name.lower())  # Convert to lowercase and remove non-alphanumeric characters
    return name

# Load the content of the RDF files
lurelu_graph = rdflib.Graph()
lurelu_graph.parse("output_lurelu.ttl", format="turtle")

bnf_graph = rdflib.Graph()
bnf_graph.parse("output_bnf.ttl", format="turtle")

constellations_graph = rdflib.Graph()
constellations_graph.parse("output_constellations.ttl", format="turtle")

# Extract book names and their corresponding subjects for easy lookup
bnf_books = {normalize_name(str(bnf_graph.value(subject, rdflib.URIRef("http://schema.org/name")))): subject for subject in bnf_graph.subjects(predicate=rdflib.RDF.type, object=rdflib.URIRef("http://schema.org/Book"))}
constellations_books = {normalize_name(str(constellations_graph.value(subject, rdflib.URIRef("http://schema.org/name")))): subject for subject in constellations_graph.subjects(predicate=rdflib.RDF.type, object=rdflib.URIRef("http://schema.org/Book"))}

# Iterate over books in lurelu_graph
for lurelu_book in lurelu_graph.subjects(predicate=rdflib.RDF.type, object=rdflib.URIRef("http://schema.org/Book")):
    lurelu_book_name = normalize_name(str(lurelu_graph.value(lurelu_book, rdflib.URIRef("http://schema.org/name"))))
    
    # Check for close matches in bnf_books and constellations_books
    matched_books = get_close_matches(lurelu_book_name, list(bnf_books.keys()) + list(constellations_books.keys()), n=1, cutoff=0.85)
    
    # If a match is found, extract the ISBN and add it to the lurelu_book
    if matched_books:
        matched_book_name = matched_books[0]
        if matched_book_name in bnf_books:
            isbn = bnf_graph.value(bnf_books[matched_book_name], rdflib.URIRef("http://schema.org/isbn"))
            if isbn:
                lurelu_graph.add((lurelu_book, rdflib.URIRef("http://schema.org/isbn"), isbn))
        elif matched_book_name in constellations_books:
            isbn = constellations_graph.value(constellations_books[matched_book_name], rdflib.URIRef("http://schema.org/isbn"))
            if isbn:
                lurelu_graph.add((lurelu_book, rdflib.URIRef("http://schema.org/isbn"), isbn))

# Save the updated output_lurelu.ttl
lurelu_graph.serialize("output_lurelu_updated.ttl", format="turtle")

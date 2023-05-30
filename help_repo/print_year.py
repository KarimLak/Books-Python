from rdflib import Graph, Namespace, RDF, Literal
import re

ns1 = Namespace("http://schema.org/")

g = Graph()

# Load file into the graph
g.parse("./final_output.ttl", format="turtle")

def find_books_starting_with_lowercase(g):
    for s in g.subjects(RDF.type, ns1.Book):
        book_name = g.value(s, ns1.name)
        if book_name and re.match(r'^[a-z]', str(book_name)):
            print(f'Book: {book_name}')

find_books_starting_with_lowercase(g)

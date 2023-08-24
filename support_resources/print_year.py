from rdflib import Graph, Namespace, RDF, Literal

ns1 = Namespace("http://schema.org/")

g = Graph()

# Load file into the graph
g.parse("./final_output.ttl", format="turtle")

def find_books_with_multiple_dates(g):
    for s in g.subjects(RDF.type, ns1.Book):
        book_name = g.value(s, ns1.name)
        dates = list(g.objects(s, ns1.dateReceived))
        if len(dates) > 1:
            print(f'Book: {book_name}, Dates received: {dates}')

find_books_with_multiple_dates(g)

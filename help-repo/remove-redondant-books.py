from rdflib import Graph, Namespace
from collections import defaultdict
from rdflib import RDF

# Define the namespace
ns1 = Namespace("http://schema.org/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

def remove_duplicate_books(filepath):
    # Parse the ttl files
    g = Graph()
    g.parse(filepath, format="turtle")

    # Create a dict to hold unique books
    unique_books = defaultdict(list)

    # Get all books from the graph
    books = [book for book in g.subjects(predicate=RDF.type, object=ns1["Book"])]

    for book in books:
        # Get all properties of the book
        properties = [str(g.value(subject=book, predicate=p)) for p in [ns1["name"], ns1["author"], ns1["publisher"], ns1["genre"], ns1["datePublished"], ns1["award"], ns1["url"]]]
        # Use properties as key to identify duplicate books
        key = tuple(properties)
        unique_books[key].append(book)

    # Remove duplicate books
    for key, books in unique_books.items():
        if len(books) > 1:
            # If there are duplicate books, keep the first one and remove the rest
            for book in books[1:]:
                for p in [ns1["name"], ns1["author"], ns1["publisher"], ns1["genre"], ns1["datePublished"], ns1["award"], ns1["url"]]:
                    g.remove((book, p, None))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

# Call the function with your ttl file name
remove_duplicate_books("./output_ricochet.ttl")

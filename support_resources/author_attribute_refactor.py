from rdflib import Graph, Namespace, Literal, XSD
import re

# Define the namespace
ns1 = Namespace("http://schema.org/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

# List of TTL files to process
filepaths = [
    "./missing_output_3.ttl"
]

for filepath in filepaths:
    # Parse the ttl files
    g = Graph()
    g.parse(filepath, format="turtle")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["author"]))

    for book in books:
        # Extract the current author
        author = g.value(subject=book, predicate=ns1["author"])
        if ' et ' in str(author) or ',' in str(author):
            print(author)
            # Split the author string and strip whitespace
            authors = [a.strip() for a in re.split(' et |,', str(author))]
            # Remove the old author
            g.remove((book, ns1["author"], None))
            # Add the new authors to the book
            for author in authors:
                g.add((book, ns1["author"], Literal(author, datatype=xsd.string)))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

from rdflib import Graph, Namespace, Literal, XSD
from datetime import datetime

# Define the namespace
ns1 = Namespace("http://schema.org/")

# List of TTL files to process
filepaths = [
    "./output-lurelu-tables.ttl",
    "./output-lurelu.ttl"
]

for filepath in filepaths:
    # Parse the ttl files
    g = Graph()
    g.parse(filepath, format="turtle")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["datePublished"]))

    for book in books:
        # Extract the current datePublished
        datePublished = g.value(subject=book, predicate=ns1["datePublished"])

        if datePublished.datatype == XSD.gYear:
            # Reduce the year by 1
            reduced_year = int(datePublished) - 1

            # Update the book's datePublished in the graph
            g.set((book, ns1["datePublished"], Literal(reduced_year, datatype=XSD.gYear)))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

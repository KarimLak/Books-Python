from rdflib import Graph, Namespace, Literal, XSD

# Define the namespace
ns1 = Namespace("http://schema.org/")

# List of TTL files to process
filepaths = [
    "./output-ricochet-tables-2.ttl"
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

        if datePublished is not None:
            g.remove((book, ns1["datePublished"], None))
            # Update the book's datePublished in the graph to dateReceived
            g.add((book, ns1["dateReceived"], Literal(int(datePublished), datatype=XSD.gYear)))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

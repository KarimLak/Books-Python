from rdflib import Graph, Namespace, Literal, URIRef

# Define the namespace
ns1 = Namespace("http://ns1.org/")
xsd1 = Namespace("http://www.w3.org/2001/XMLns1#")

# List of TTL files to process
filepaths = [
    "./output_ricochet.ttl"
]

for filepath in filepaths:
    # Parse the ttl files
    g = Graph()
    g.bind("ns1", ns1)
    g.bind("xsd1", xsd1)
    
    g.parse(filepath, format="turtle")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["datePublished"]))

    for book in books:
        # Extract the current datePublished
        datePublished = g.value(subject=book, predicate=ns1["datePublished"])

        if datePublished is not None:
            g.remove((book, ns1["datePublished"], None))
            # Update the book's datePublished in the graph to dateReceived
            if isinstance(datePublished, Literal) and datePublished.datatype == xsd1.gYear:
                g.add((book, ns1["dateReceived"], Literal(int(datePublished), datatype=xsd1.gYear)))
            else:
                g.add((book, ns1["dateReceived"], Literal(str(datePublished))))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

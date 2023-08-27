from rdflib import Graph, Namespace, Literal, XSD
import re

# Define the namespace
ns1 = Namespace("http://schema.org/")

# List of TTL files to process
filepaths = [
    "./output-prixdeslibraires-bd.ttl",
    "./output-prixdeslibraires-essai.ttl",
    "./output-prixdeslibraires-jeunesse.ttl",
    "./output-prixdeslibraires-poesie.ttl",
    "./output-prixdeslibraires-roman.ttl"
]

# Prefix to add
prefix = "Prix des libraires : "

for filepath in filepaths:
    # Parse the ttl files
    g = Graph()
    g.parse(filepath, format="turtle")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["award"]))

    for book in books:
        # Extract the current award and update the book's award in the graph
        award = g.value(subject=book, predicate=ns1["award"])
        if award and not str(award).startswith(prefix):
            new_award = prefix + str(award)
            g.set((book, ns1["award"], Literal(new_award, datatype=XSD.string)))

    # Update description
    descriptions = list(g.subject_objects(predicate=ns1["description"]))
    for book, description in descriptions:
        # Update the book's description in the graph if it starts with 'Préliminaire', 'Finaliste', or 'Lauréat'
        if description and re.match(r"^(Préliminaire|Finaliste|Lauréat)", str(description)) and not str(description).startswith(prefix):
            new_description = prefix + str(description)
            g.set((book, ns1["description"], Literal(new_description, datatype=XSD.string)))

    # Serialize the updated graph
    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

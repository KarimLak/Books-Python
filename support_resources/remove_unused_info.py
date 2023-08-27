from rdflib import Graph, Namespace, Literal

# Define the namespace
ns1 = Namespace("http://schema.org/")

# Parse the ttl file
g = Graph()
g.parse("./output-ricochet.ttl", format="turtle")

# Get all books from the graph
books = list(g.subjects(predicate=ns1["author"]))

for book in books:
    # Extract the current author
    author = g.value(subject=book, predicate=ns1["author"])

    # Extract the name
    name = g.value(subject=book, predicate=ns1["name"])

    # If author is equal to name, remove the specified attributes
    if author == name:
        for predicate in [ns1['datePublished'], ns1['genre'], ns1['inLanguage'], ns1['name'], ns1['publisher']]:
            g.remove((book, predicate, None))

# Serialize the updated graph
output_data = g.serialize(format="turtle")

# Write the updated data back to the TTL file
with open("./output-ricochet.ttl", "w", encoding="utf-8") as f: # Open the file in binary mode
    f.write(output_data)

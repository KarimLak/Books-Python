from rdflib import Graph, Namespace, Literal

# Load the RDF data from the file
g = Graph()
g.parse("output_bnf_2_updated.ttl", format="turtle")

# Define the namespaces
ns1 = Namespace("http://schema.org/")

# Collect the publishers
publishers = set()
for _, _, publisher in g.triples((None, ns1.publisher, None)):
    if isinstance(publisher, Literal) and publisher.language is None:
        publishers.add(publisher)

# Convert the set to a sorted list
sorted_publishers = sorted(publishers)

# Write the sorted publishers to a new file
with open("publishers.txt", "w", encoding="utf-8") as f:
    for publisher in sorted_publishers:
        f.write(f"{publisher}\n")

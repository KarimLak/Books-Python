from rdflib import Graph, Namespace, Literal, RDF
import glob

# Define the namespaces
MCC = Namespace("http://example.com/mcc#")
PBS = Namespace("http://example.com/pbs#")
SCHEMA = Namespace("http://schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# Create an empty graph
graph = Graph()

# Load the RDF data from the awards and hierarchy_representation_awards files
graph.parse("./awards.ttl", format="turtle")
graph.parse("./hierarchy_representation_awards.ttl", format="turtle")

def has_description(node):
    """
    Check if a given node has a description.
    """
    if (node, SCHEMA.description, None) in graph:
        return True
    return False

def find_parent(node):
    """
    Find the parent of a given node.
    """
    for parent in graph.objects(None, SKOS.narrower):
        if node in parent:
            return parent
    return None

# Iterate over all awards
for award in graph.subjects(RDF.type, MCC['MCC-E12']):
    parent = find_parent(award)
    grandparent = find_parent(parent) if parent else None

    if parent and grandparent:
        if not has_description(parent) and not has_description(grandparent):
            # If neither the parent nor the grandparent has a description, print the book URI
            book_uri = graph.value(award, MCC['R37'])
            print(book_uri)

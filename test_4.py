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

def has_genre(node):
    """
    Check if a given node has a genre.
    """
    if (node, PBS.genreLittéraire, None) in graph:
        return True
    return False

def find_parent(node):
    """
    Find the parent of a given node.
    """
    for parent in graph.subjects(SKOS.narrower, node):
        return parent
    return None

# Create a set to hold the seen parents
seen_parents = set()

# Iterate over all awards
for award in graph.subjects(RDF.type, MCC['MCC-E12']):
    parent = find_parent(award)
    grandparent = find_parent(parent) if parent else None
    great_grandparent = find_parent(grandparent) if grandparent else None

    if parent and grandparent and great_grandparent:
        if not has_description(parent) and not has_description(grandparent) and not has_genre(great_grandparent):
            # If either the parent or the grandparent doesn't have a description, or the great grandparent doesn't have a genre, print the parent URI
            if parent not in seen_parents:
                print(parent)
                seen_parents.add(parent)

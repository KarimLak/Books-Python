from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

# Load your files
awards_graph = Graph()
awards_graph.parse('awards.ttl', format='turtle')

hierarchy_graph = Graph()
hierarchy_graph.parse('hierarchy_representation_awards.ttl', format='turtle')

# Define your namespace
pbs = Namespace('http://example.com/pbs#')
mcc = Namespace('http://example.com/mcc#')

# Get all the awards of type MCC-E12 in the awards file
awards_to_remove = set()
for subj, _, _ in awards_graph.triples((None, None, mcc['MCC-E12'])):
    awards_to_remove.add(subj)

# Iterate over the triples in your hierarchy file
for subj, pred, obj in list(hierarchy_graph.triples((None, SKOS.narrower, None))):
    # If the object (award) is in the set of awards to remove, delete the triple
    if obj in awards_to_remove:
        hierarchy_graph.remove((subj, pred, obj))

# Serialize the modified graph back to turtle
hierarchy_graph.serialize(destination='modified_hierarchy.ttl', format='turtle')

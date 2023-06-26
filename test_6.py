from rdflib import Graph, Namespace, URIRef
import hashlib

# Define your namespaces
ns1 = Namespace("http://schema.org/")
mcc = Namespace("http://example.com/mcc#")

# Load your graph
g = Graph()
g.parse("./awards.ttl", format="turtle")

# Store all unique awards
unique_awards = set()

# Iterate over all awards
for s in g.subjects(predicate=mcc["R37"]):
    award_properties = []

    # Iterate over all properties of an award
    for p, o in g.predicate_objects(subject=s):
        award_properties.append(str(p))
        award_properties.append(str(o))

    # Generate a unique key for the award
    award_key = hashlib.sha1(''.join(sorted(award_properties)).encode()).hexdigest()

    # If the key is already in the set, remove the award
    if award_key in unique_awards:
        for p in list(g.predicates(subject=s)):
            g.remove((s, p, None))
    else:
        unique_awards.add(award_key)

# Save the modified graph
g.serialize(destination='./awards.ttl', format='turtle')

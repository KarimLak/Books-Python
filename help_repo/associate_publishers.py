from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from difflib import SequenceMatcher

# Function to find the best matching publisher
def best_matching_publisher(publisher, publisher_list):
    best_match = publisher
    best_ratio = 0

    for candidate in publisher_list:
        ratio = SequenceMatcher(None, publisher, candidate).ratio()
        if ratio > best_ratio:
            best_match = candidate
            best_ratio = ratio

    return best_match

# Load the main data graph
g_main = Graph()
g_main.parse("./merged_output.ttl", format="turtle")

# Load the publishers graph
g_publishers = Graph()
g_publishers.parse("./publishers_conversion.ttl", format="turtle")

ns1 = Namespace("http://schema.org/")

# A dictionary to cache publisher URIs for faster lookup
publisher_uris = {}

# List of all publisher names in the publishers graph
publisher_names = [str(name) for s, p, name in g_publishers.triples((None, ns1.name, None))]

# Iterate over the books
for s, p, o in g_main.triples((None, RDF.type, ns1.Book)):
    # Get the current publisher name
    publisher_name = str(g_main.value(s, ns1.publisher))

    if publisher_name in publisher_uris:
        # If we've seen this publisher before, just get the URI from the cache
        publisher_uri = publisher_uris[publisher_name]
    else:
        # Otherwise, find the corresponding publisher URI in the publishers graph
        publisher_uri = None
        for s_pub, p_pub, o_pub in g_publishers.triples((None, ns1.name, None)):
            if str(o_pub) == publisher_name:
                publisher_uri = s_pub
                break

        if not publisher_uri:
            # If no match found, find the closest matching publisher
            closest_match = best_matching_publisher(publisher_name, publisher_names)

            # Get the URI of the closest matching publisher
            for s_pub, p_pub, o_pub in g_publishers.triples((None, ns1.name, None)):
                if str(o_pub) == closest_match:
                    publisher_uri = s_pub
                    break

            print(f"No exact match found for publisher '{publisher_name}', closest match is '{closest_match}'")

        if publisher_uri:
            # If we found a matching publisher URI, store it in the cache for future use
            publisher_uris[publisher_name] = publisher_uri

    if publisher_uri:
        # If we found a matching publisher URI, replace the publisher name with it
        g_main.set((s, ns1.publisher, publisher_uri))

# Save the updated main graph
g_main.serialize(destination='updated_output.ttl', format='turtle')

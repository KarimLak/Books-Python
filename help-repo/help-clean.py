from rdflib import Graph, Namespace, Literal, XSD
import urllib.parse

# Define the namespace
ns1 = Namespace("http://schema.org/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

def convert_url_to_string(ttl_filepath, output_filepath):
    # Parse the ttl files
    g = Graph()
    g.parse(ttl_filepath, format="turtle")

    # Create a new graph to hold updated triples
    new_g = Graph()

    # Go through each triple in the graph
    for s, p, o in g:
        # If the predicate is 'url', change the object to a string literal
        if p == ns1['url']:
            o = Literal(urllib.parse.unquote(str(o)), datatype=xsd.string)
        new_g.add((s, p, o))

    # Serialize the updated graph to turtle format
    output_data = new_g.serialize(format="turtle")

    # Write the updated data to the output TTL file
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

# Call the function with your ttl file name and output file name
convert_url_to_string("./output-ricochet-tables-2.ttl", "./output-ricochet-tables-2.ttl")

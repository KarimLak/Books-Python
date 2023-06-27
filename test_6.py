from rdflib import Graph, Namespace, XSD

# Define your namespaces
ns1 = Namespace("http://schema.org/")

# Load your graph
g = Graph()
g.parse("./books.ttl", format="turtle")

# Define your SPARQL query
query = """
    SELECT DISTINCT ?book WHERE {
        ?book a ns1:Book .
        OPTIONAL { ?book ns1:author ?author . }
        OPTIONAL { ?book ns1:illustrator ?illustrator . }
        OPTIONAL { ?book ns1:inLanguage ?inLanguage . }
        OPTIONAL { ?book ns1:name ?name . }
        OPTIONAL { ?book ns1:publisher ?publisher . }
        OPTIONAL { ?book ns1:countryOfOrigin ?countryOfOrigin . }
        FILTER ((!bound(?author) && !bound(?illustrator)) || !bound(?inLanguage) || (!bound(?publisher) && !bound(?countryOfOrigin)) || !bound(?name))
    }
"""
# Run your query
result = g.query(query, initNs={"ns1": ns1})

# Print the URIs of the books that are missing any of those properties
for row in result:
    print(row[0])

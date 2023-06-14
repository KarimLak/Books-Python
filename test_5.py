import rdflib

# Load the awards graph
awards = rdflib.Graph()
awards.parse("./awards.ttl", format="ttl")

# Define the namespaces
mcc = rdflib.Namespace("http://example.com/mcc#")
schema = rdflib.Namespace("http://schema.org/")

# Find awards without mcc:R37 attribute
awards_without_r37 = awards.query('''
    SELECT ?award {
        ?award a mcc:MCC-E12 ;
               ?p ?o .
        FILTER NOT EXISTS { ?award mcc:R37 ?book }
    }
''')

# Print the URIs of the awards without mcc:R37 attribute
for row in awards_without_r37:
    award = row['award']
    print(award)

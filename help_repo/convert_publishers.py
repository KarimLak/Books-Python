import csv
import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS

# Create a graph
g = rdflib.Graph()

# Define namespaces
schema = Namespace('http://schema.org/')
xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

# Read organizations from CSV file
with open('./publishers.csv', 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    orgs = [row[0] for row in reader]

for org in orgs:
    org_name = org.replace(' ', '_')
    org_uri = URIRef(f'{schema}{org_name}')
    g.add((org_uri, RDF.type, schema.Organization))
    g.add((org_uri, schema.name, Literal(org, datatype=xsd.string)))

# Serialize the graph in Turtle format and write it to a file
with open('./publishers_conversion.ttl', 'w', encoding="utf-8") as f:
    f.write(g.serialize(format='turtle'))

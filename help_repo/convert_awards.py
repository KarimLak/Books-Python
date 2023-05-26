import csv
import rdflib
import re
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS

# Create a graph
g = rdflib.Graph()

# Define namespaces
schema = Namespace('http://schema.org/')
xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

# Parent-Child relationships
parent_orgs = {
    "Biennale De L'illustration De Bratislava : Grand Prix" : "Biennale De L'illustration De Bratislava"
}

# Regular expression to match non-alphanumeric characters, with exceptions
pattern = re.compile(r'[^a-zA-Z0-9À-ÖØ-öø-ÿ]+')

# Read organizations from CSV file
with open('./awards.csv', 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    orgs = [row[0] for row in reader]

for org in orgs:
    # Replace sequences of non-alphanumeric characters with a single underscore
    org_name = pattern.sub('_', org)
    org_uri = URIRef(f'{schema}{org_name}')
    g.add((org_uri, RDF.type, schema.Organization))
    g.add((org_uri, schema.name, Literal(org, datatype=xsd.string)))

    # Check if org has parent organization
    if org in parent_orgs:
        parent_org = parent_orgs[org]
        parent_org_name = pattern.sub('_', parent_org)
        parent_org_uri = URIRef(f'{schema}{parent_org_name}')
        g.add((org_uri, schema.parentOrganization, parent_org_uri))
        g.add((parent_org_uri, schema.subOrganization, org_uri))

# Serialize the graph in Turtle format and write it to a file
with open('./awards_conversion.ttl', 'w', encoding="utf-8") as f:
    f.write(g.serialize(format='turtle'))

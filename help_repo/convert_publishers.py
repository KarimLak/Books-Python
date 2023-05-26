import csv
import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS

# Create a graph
g = rdflib.Graph()

# Define namespaces
schema = Namespace('http://schema.org/')
xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

# Parent-Child relationships
parent_orgs = {
    'Actes Sud Bd': 'Actes Sud',
    'Actes Sud Junior': 'Actes Sud',
    'Actes Sud-Papiers': 'Actes Sud',
    'Albin Michel Jeunesse' : 'Albin Michel',
    'Alice Jeunesse' : 'Alice',
    'Albin Jeunesse' : 'Albin',
    'Autrement Jeunesse' : 'Autrement',
    'Auzou Canada' : 'Anzou',
    'Auzou Suisse' : 'Anzou',
    'Bayard Canada' : 'Bayard',
    'Bayard Jeunesse' : 'Bayard',
    'Belin Jeunesse' : 'Belin',
    'Cappelen Damm' : 'Cappelen',
    'Cappelen Forlag' : 'Cappelen',
    'Casterman Poche' : 'Casterman',
    'Didier Jeunesse' : 'Didier',
    'Flammarion Jeunesse' : 'Flammarion',
    'Flammarion Père Castor' : 'Flammarion',
    'Castor Poche Flammarion' : 'Flammarion',
    'Gallimard Jeunesse' : 'Gallimard',
    'Glénat Jeunesse' : 'Glénat',
    'Grasset Jeunesse' : 'Grasset',
    'Hachette Jeunesse' : 'Hachette',
    'HongFei Cultures' : 'HongFei',
    'Kazé Manga' : 'Kazé',
    'La Martinière Jeunesse' : 'La Martinière',
    'Lansman Jeunesse' : 'Lansman',
    'Magnard Jeunesse' : 'Magnard',
    'Mango Jeunesse' : 'Mango',
    'Milan Jeunesse' : 'Milan',
    'Milan Poche' : 'Milan',
    'Nathan Jeunesse' : 'Nathan',
    'Nathan Poche' : 'Nathan',
    'Oskar Jeunesse' : 'Oskar',
    'Panama Jeunesse' : 'Panama',
    'Pocket Jeunesse' : 'Pocket',
    'Pocket Junior' : 'Pocket',
    'Puffin Canada' : 'Puffin',
    'Samir Jeunesse' : 'Samir',
    'Scholastic Canada' : 'Scholastic',
    'Scrineo Jeunesse' : 'Scrineo',
    'Seuil Poche' : 'Seuil',
    'Seuil-Le Funambule' : 'Seuil',
    'Seuil Jeunesse' : 'Seuil',
    'Stoddart Kids' : 'Stoddart',
    'Versant Sud Jeunesse' : 'Versant Sud'
}

# Read organizations from CSV file
with open('./publishers.csv', 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    orgs = [row[0] for row in reader]

for org in orgs:
    # Replace spaces, '&', and '/' with underscores and remove apostrophes
    org_name = org.replace(' ', '_').replace("'", "").replace("&", "_").replace("/", "_").replace(".", "")
    org_uri = URIRef(f'{schema}{org_name}')
    g.add((org_uri, RDF.type, schema.Organization))
    g.add((org_uri, schema.name, Literal(org, datatype=xsd.string)))

    # Check if org has parent organization
    if org in parent_orgs:
        parent_org_name = parent_orgs[org].replace(' ', '_').replace("'", "").replace("&", "_").replace("/", "_").replace(".", "")
        parent_org_uri = URIRef(f'{schema}{parent_org_name}')
        g.add((org_uri, schema.parentOrganization, parent_org_uri))
        g.add((parent_org_uri, schema.subOrganization, org_uri))

# Serialize the graph in Turtle format and write it to a file
with open('./publishers_conversion.ttl', 'w', encoding="utf-8") as f:
    f.write(g.serialize(format='turtle'))
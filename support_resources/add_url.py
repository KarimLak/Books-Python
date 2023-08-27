from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import uuid

# Initialize the namespace
ns1 = Namespace("http://ns1.org/")

def update_uris(file_path):
    # Load the RDF graph
    g = Graph()
    g.parse(file_path, format='turtle')

    # Collect all pre-existing URIs
    existing_uris = {str(book) for book in g.subjects(RDF.type, ns1.Book)}

    # Loop through each book and update its URI
    for book in existing_uris:
        old_uri = URIRef(book)

        # Generate a new URI
        new_uri = ns1[f'Book_{old_uri.localName}_{uuid.uuid4()}']

        # Update the triples with the new URI
        for p, o in g.predicate_objects(old_uri):
            g.remove((old_uri, p, o))
            g.add((new_uri, p, o))

    # Save the updated RDF graph
    g.serialize(destination=file_path, format='turtle')

# Call the function with the path to your RDF file
update_uris("./missing_output.ttl")

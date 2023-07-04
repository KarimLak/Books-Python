from rdflib import Graph, Literal, URIRef, Namespace, BNode, RDF
from uuid import uuid4

# Define your namespaces
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.com/pbs#")
mcc = Namespace("http://example.com/mcc#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
schema = Namespace("http://schema.org/")

# Create a new graph and parse in an existing ttl file
g = Graph()
g.parse("./missing_outputs.ttl", format="turtle")

# Create a new graph for output
g_output = Graph()

# Loop over all books in the graph
for book in g.subjects(RDF.type, ns1.Book):
    # If the book has the award you're interested in
    if (book, ns1.award, Literal("PRIX ACELF")) in g:
        # Get the year the book received the award
        year = g.value(book, ns1.dateReceived)

        # Create a new award instance with a unique identifier
        award_id = URIRef(f"http://example.com/pbs#Prix_Acelf{uuid4().hex}")
        g_output.add((award_id, RDF.type, mcc['MCC-E12']))

        if year is not None:
            g_output.add((award_id, mcc['MCC-R35-4'], Literal(year, datatype=xsd.gYear)))

        # Extract the book ID from the book URI and create a new URIRef in the format you want
        book_id = URIRef(book.split('/')[-1])
        book_id_formatted = URIRef(f"{schema}{book_id}")
        g_output.add((award_id, mcc.R37, book_id_formatted))
        
        g_output.add((award_id, pbs.award, URIRef("http://example.com/pbs#Prix_Acelf")))

# Bind the namespaces
g_output.bind("mcc", mcc)
g_output.bind("pbs", pbs)
g_output.bind("schema", schema)

# Serialize the new graph to turtle and write to file
g_output.serialize(destination='output.ttl', format='turtle')

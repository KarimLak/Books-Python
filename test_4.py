import rdflib

# Load the books and awards graphs
books = rdflib.Graph()
books.parse("./books.ttl", format="ttl")

awards = rdflib.Graph()
awards.parse("./awards.ttl", format="ttl")

# Define the namespaces
ns1 = rdflib.Namespace("http://schema.org/")
pbs = rdflib.Namespace("http://example.com/pbs#")
mcc = rdflib.Namespace("http://example.com/mcc#")

# Get all the books in the books file
book_resources = list(books.subjects(predicate=rdflib.RDF.type, object=ns1.Book))

for book in book_resources:
    # Remove the old awards properties
    old_awards = list(books.objects(subject=book, predicate=ns1.award))
    for award in old_awards:
        books.remove((book, ns1.award, award))

    # Convert the book to a string format and remove 'ns1:' prefix
    book_str = str(book).replace('ns1:', 'schema:')

    # Get the award resources in the awards file that match the book
    award_resources = list(awards.subjects(predicate=mcc.R37, object=rdflib.URIRef(book_str)))

    for award_resource in award_resources:
        # Get the actual award name that the award_resource points to
        award = awards.value(subject=award_resource, predicate=pbs.award)

        # Get the award name
        award_name = awards.value(subject=award, predicate=ns1.name)

        # Add the new award property to the book
        if award_name is not None:
            books.add((book, ns1.award, rdflib.Literal(award_name)))

# Save the modified books file
books.serialize(destination="./books_updated.ttl", format="ttl")
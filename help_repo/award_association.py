from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from fuzzywuzzy import process
import uuid
from unidecode import unidecode

# Namespaces
ns1 = Namespace("http://schema.org/")

# Load the books graph
books_g = Graph()
books_g.parse("./final_output_merged.ttl", format="turtle", encoding="utf-8")

# Load the awards graph
awards_g = Graph()
awards_g.parse("./awards_conversion.ttl", format="turtle", encoding="utf-8")

# Create a dictionary of all award names and their URIs
award_dict = {unidecode(str(name).lower().strip()): str(s) for s, _, name in awards_g.triples((None, ns1.name, None))}

# Generate awards
for s in books_g.subjects(RDF.type, ns1.Book):
    # Get the book's information
    book_name = str(books_g.value(s, ns1.name))
    authors = list(books_g.objects(s, ns1.author))
    date_received = str(books_g.value(s, ns1.dateReceived)) or str(books_g.value(s, ns1.datePublished))
    awards = list(books_g.objects(s, ns1.award))

    # For each award, check if we have a corresponding URI in the dictionary
    for award in awards:
        # Normalize the award name
        award_norm = unidecode(award.lower().strip())
        
        if award_norm in award_dict:
            main_award_uri = URIRef(award_dict[award_norm])
        else:
            print(f"No match found in awards_conversion.ttl for award: {award}")
            continue

        # Generate a unique URI for the sub award
        sub_award_uri = URIRef(str(main_award_uri) + str(uuid.uuid4()))

        # Add the sub award to the awards graph
        awards_g.add((sub_award_uri, RDF.type, ns1.Award))
        awards_g.add((sub_award_uri, getattr(ns1, 'for'), Literal(book_name)))
        for author in authors:
            awards_g.add((sub_award_uri, ns1.to, Literal(author)))
        awards_g.add((sub_award_uri, ns1.date, Literal(date_received)))

        # Link the main award to the sub award
        awards_g.add((main_award_uri, ns1.subOrganization, sub_award_uri))

# Save the updated awards graph
awards_g.serialize(destination='./awards_conversion_final.ttl', format='turtle', encoding="utf-8")

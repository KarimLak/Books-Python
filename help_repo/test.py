from rdflib import Graph, Namespace, Literal, RDF
from unidecode import unidecode

# Namespaces
ns1 = Namespace("http://schema.org/")

# Load the books graph for merged_output
merged_output_g = Graph()
merged_output_g.parse("./merged_output.ttl", format="turtle", encoding="utf-8")

# Load the books graph for final_output_merged_final
final_g = Graph()
final_g.parse("./final_output_merged_final.ttl", format="turtle", encoding="utf-8")

# Load the awards graph for awards_conversion_final
awards_g = Graph()
awards_g.parse("./awards_conversion_final.ttl", format="turtle", encoding="utf-8")

# Check for multiple authors in merged_output and single author in final_output_merged_final
for s in merged_output_g.subjects(RDF.type, ns1.Book):
    # Get the book's information
    book_name = str(merged_output_g.value(s, ns1.name))
    normalized_book_name = unidecode(book_name.lower())
    merged_authors = list(merged_output_g.objects(s, ns1.author))

    if len(merged_authors) > 1:
        # Find the same book in final_output_merged_final
        final_book = None
        for subj in final_g.subjects():
            final_book_name = str(final_g.value(subj, ns1.name))
            if normalized_book_name == unidecode(final_book_name.lower()):
                final_book = subj
                break
        
        if final_book is not None:
            final_authors = list(final_g.objects(final_book, ns1.author))
            if len(final_authors) != len(merged_authors):
                # Remove the existing author(s) for the book in final_output_merged_final
                final_g.remove((final_book, ns1.author, None))
                # Add the correct author(s) for the book in final_output_merged_final
                for author in merged_authors:
                    final_g.add((final_book, ns1.author, Literal(author)))

                # Adjust the author(s) for the book's awards in awards_conversion_final
                for award in final_g.objects(final_book, ns1.award):
                    # Remove the existing author(s) for the award
                    awards_g.remove((award, ns1.to, None))
                    # Add the correct author(s) for the award
                    for author in merged_authors:
                        awards_g.add((award, ns1.to, Literal(author)))

# Save the updated graphs
final_g.serialize(destination='./final_output_merged_final.ttl', format='turtle', encoding="utf-8")
awards_g.serialize(destination='./awards_conversion_final.ttl', format='turtle', encoding="utf-8")

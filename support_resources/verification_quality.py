from rdflib import Graph, Namespace
from rdflib.namespace import RDF
import re

# Initialize the namespace
ns1 = Namespace('http://schema.org/')

def check_book_attributes(file_path):
    # Load the RDF graph
    g = Graph()
    g.parse(file_path, format='turtle')

    # Open an output file to write the URIs that do not meet the criteria
    with open('invalid_books.txt', 'w') as f:

        # Loop through each book in the graph
        for s, _, _ in g.triples((None, RDF.type, ns1.Book)):

            # Collect all the predicates and objects for this book
            attributes = list(g.predicate_objects(s))

             # Check if there are at least 6 attributes
            #if len(attributes) < 6:
               #  f.write(str(s) + '\n')
                # continue

            # Check if the author or publisher contains ' or ( or ) or -
            # for p, o in attributes:
            #     if p == ns1.author:
            #         if any(c in str(o) for c in ["(", ")"]):
            #             f.write(str(s) + '\n')
            #             continue

             # Check if there are multiple names for the book
            names = list(g.objects(s, ns1.name))
            if len(names) > 1:
                  f.write(str(s) + '\n')
                  continue

             # Check if there are multiple consecutive upcases in author or name
            #for p, o in attributes:
              #   if p == ns1.author:
                 #    if re.search(r'[A-Z]{2,}', str(o)):
                   #      f.write(str(s) + '\n')

# Call the function with the path to your RDF file
check_book_attributes("./merged_output.ttl")

from rdflib import Graph, Namespace, RDF

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# Path to the input file
input_file = "./final_output_merged.ttl"

# Create a new graph and load the file into it
g = Graph()
g.parse(input_file, format="turtle")

# Initialize an empty list to hold book names with multiple publishers
books_with_multiple_publishers = []

# Iterate through all books
for s in g.subjects(RDF.type, ns1.Book):
    # Get the book's name
    book_name = g.value(s, ns1.name)
    
    # Get all the publishers for the book
    publishers = list(g.objects(s, ns1.publisher))
    
    # Check if the book has multiple publishers
    if len(publishers) > 1:
        books_with_multiple_publishers.append(str(book_name))

# Print book names with multiple publishers
for book_name in books_with_multiple_publishers:
    print(book_name)

from rdflib import Graph, Namespace, RDF

# Define the namespaces
NS1 = Namespace("http://schema.org/")
PBS = Namespace("http://www.example.org/pbs/#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Load the graphs
books_graph = Graph()
books_graph.parse("./final_datasets/bnf.ttl", format="turtle")

reviews_graph = Graph()
reviews_graph.parse("simplified_reviews.ttl", format="turtle")  # replace 'reviews.ttl' with your actual file name

# Iterate through the reviews
for review in reviews_graph.subjects(RDF.type, PBS.Review):
    # Get the associated book of the review
    book = reviews_graph.value(subject=review, predicate=PBS.reviewedBook)
    
    if book:
        # Check if the book has a pbs:avisDate attribute
        avis_date = books_graph.value(subject=book, predicate=PBS.avisDate)

        # If there's no pbs:avisDate for the book, remove ns1:datePublished from the review
        if not avis_date:
            reviews_graph.remove((review, NS1.datePublished, None))

# Save the modified reviews graph
reviews_graph.serialize(destination="updated_reviews.ttl", format="turtle")

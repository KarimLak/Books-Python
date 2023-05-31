from rdflib import Graph, Namespace, Literal, RDF
from Levenshtein import distance
import re
from collections import defaultdict

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# Function to clean string
def clean_string(s):
    s = re.sub(r'\W+', '', s)  # Remove all non-alphanumeric characters
    return s.lower()

# Path to the input file
input_file = "./final_output_merged.ttl"

# Create a new graph and load the file into it
g = Graph()
g.parse(input_file, format="turtle")

# Gather all book names and author names
books = []

for s in g.subjects(RDF.type, ns1.Book):
    book_name = g.value(s, ns1.name)
    author_name = g.value(s, ns1.author)

    if book_name and author_name:
        books.append({
            "uri": s,
            "name": str(book_name),
            "author": str(author_name),
            "similar_books": []
        })

# Calculate Levenshtein distance for each pair of book names and author names
for i in range(len(books)):
    for j in range(i + 1, len(books)):
        book_name_distance = distance(clean_string(books[i]["name"]), clean_string(books[j]["name"]))
        author_name_distance = distance(clean_string(books[i]["author"]), clean_string(books[j]["author"]))

        if book_name_distance <= 2 and author_name_distance <= 2:
            books[i]["similar_books"].append(books[j])
            books[j]["similar_books"].append(books[i])

# Merge books with similar names and authors
merged_books = 0
for book in books:
    if book["similar_books"]:
        canonical_uri = book["uri"]
        for similar_book in book["similar_books"]:
            # Transfer all properties to the canonical URI
            for p, o in g.predicate_objects(similar_book["uri"]):
                # Skip name and author properties as we're keeping the first book's
                if p not in [ns1.name, ns1.author]:
                    if not any(o2 == o for o2 in g.objects(canonical_uri, p)):
                        g.add((canonical_uri, p, o))

            # Remove the merged book from the graph
            g.remove((similar_book["uri"], None, None))
            merged_books += 1

        # After all similar books have been merged, we reassert the original name and author properties
        g.add((canonical_uri, ns1.name, Literal(book["name"])))
        g.add((canonical_uri, ns1.author, Literal(book["author"])))

        print(f'Book: {book["name"]} has an author: {book["author"]} with similar books: {", ".join([b["name"] for b in book["similar_books"]])}')

print(f'Merged {merged_books} books.')

# Save the merged graph
#g.serialize(destination='./final_output_merged.ttl', format='turtle')

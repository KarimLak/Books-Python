from rdflib import Graph, Namespace, Literal, RDF, URIRef
from Levenshtein import distance
import re
from collections import defaultdict

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# Function to clean string
def clean_string(s):
    s = re.sub(r'\W+', '', s)  # Remove all non-alphanumeric characters
    return s.lower()

# Path to the input files
input_file = "./1_final_output_merged_final_demo.ttl"
awards_file = "./new_awards.ttl"

# Create a new graph and load the book file into it
g = Graph()
g.parse(input_file, format="turtle")

# Create a new graph and load the awards file into it
g_awards = Graph()
g_awards.parse(awards_file, format="turtle")

# Gather all book names and author names
books = []
uri_mapping = defaultdict(str)

for s in g.subjects(RDF.type, ns1.Book):
    book_name = g.value(s, ns1.name)
    author_names = list(g.objects(s, ns1.author))

    if book_name and author_names:
        books.append({
            "uri": s,
            "name": str(book_name),
            "authors": author_names,
            "similar_books": []
        })

# Calculate Levenshtein distance for each pair of book names and author names
for i in range(len(books)):
    for j in range(i + 1, len(books)):
        book_name_distance = distance(clean_string(books[i]["name"]), clean_string(books[j]["name"]))
        author_name_distance = distance(clean_string(books[i]["authors"][0]), clean_string(books[j]["authors"][0]))

        if book_name_distance <= 1 and author_name_distance <= 2:
            books[i]["similar_books"].append(books[j])
            books[j]["similar_books"].append(books[i])

# Merge books with similar names and authors
merged_books = 0
for book in books:
    if book["similar_books"]:
        canonical_uri = book["uri"]
        # Keep the authors from the book with the most authors
        max_authors = max([len(b["authors"]) for b in [book] + book["similar_books"]])
        authors_to_keep = [b["authors"] for b in [book] + book["similar_books"] if len(b["authors"]) == max_authors][0]

        for similar_book in book["similar_books"]:
            # Transfer all properties to the canonical URI
            for p, o in g.predicate_objects(similar_book["uri"]):
                # Skip name and author properties as we're keeping the first book's
                if p not in [ns1.name, ns1.author]:
                    if not any(o2 == o for o2 in g.objects(canonical_uri, p)):
                        g.add((canonical_uri, p, o))

            # Store the old and new URI
            uri_mapping[str(similar_book["uri"])] = str(canonical_uri)

            # Remove the merged book from the graph
            g.remove((similar_book["uri"], None, None))
            merged_books += 1

        # After all similar books have been merged, we reassert the original name and author properties
        g.add((canonical_uri, ns1.name, Literal(book["name"])))
        for author in authors_to_keep:
            g.add((canonical_uri, ns1.author, author))

        print(f'Book: {book["name"]} has authors: {", ".join([str(a) for a in authors_to_keep])} with similar books: {", ".join([b["name"] for b in book["similar_books"]])}')

print(f'Merged {merged_books} books.')

# Save the merged graph
g.serialize(destination='./1_final_output_merged_final_demo.ttl', format='turtle')

# Replace old URIs with new ones in the awards graph
for s, p, o in g_awards:
    if str(o) in uri_mapping:
        g_awards.remove((s, p, o))
        g_awards.add((s, p, URIRef(uri_mapping[str(o)])))

# Save the updated awards graph
g_awards.serialize(destination='./new_awards.ttl', format='turtle')

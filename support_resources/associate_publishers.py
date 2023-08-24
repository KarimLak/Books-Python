from rdflib import Graph, Namespace, Literal, RDF
from unidecode import unidecode
import os
import re
from collections import defaultdict

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# List of input file paths
input_files = [
    "./1_final_output_merged_final_demo.ttl"
]

# Create a new graph
g = Graph()

# Load all files into the graph
for file in input_files:
    if os.path.exists(file):
        g.parse(file, format="turtle")

# Function to clean string
def clean_string(s):
    s = unidecode(s)
    s = re.sub(r'\W+', '', s)  # Remove all non-alphanumeric characters
    return s.lower()

# Function to group similar books
def group_similar_books(g):
    groups = defaultdict(list)

    for s in g.subjects(RDF.type, ns1.Book):
        book_name = g.value(s, ns1.name)
        book_author = g.value(s, ns1.author)

        if book_name and book_author:
            key = (clean_string(str(book_name)), clean_string(str(book_author)))
            groups[key].append((s, book_name, book_author))

    return groups

def remove_duplicate_attributes(g):
    for s in g.subjects(RDF.type, ns1.Book):
        predicates = set(g.predicates(s, None))
        for p in predicates:
            values = list(g.objects(s, p))
            if len(values) > 1:
                # Collect unique string values
                unique_values = list(set(str(v) for v in values))
                # If there are duplicates (length of set is less than length of original list)
                if len(unique_values) < len(values):
                    # Remove all instances of this predicate from the graph
                    g.remove((s, p, None))
                    # Then add back only the unique ones
                    for v in unique_values:
                        # Get the original literal with this string value
                        original_literal = next(val for val in values if str(val) == v)
                        g.add((s, p, original_literal))


# Group similar book names
similar_books = group_similar_books(g)

# Counter for merged books
merged_books = 0

# Merge books with similar names
for (book_name, book_author), similar in similar_books.items():
    if len(similar) > 1:
        existing_book, original_name, original_author = similar[0]

        for similar_book, _, _ in similar[1:]:
            # Merge similar book into the existing book
            for p, o in g.predicate_objects(similar_book):
                if p not in [ns1.author, ns1.name]:
                    if not any(o2 == o for o2 in g.objects(existing_book, p)):
                        g.add((existing_book, p, o))

            # Remove the similar book from the graph
            g.remove((similar_book, None, None))

            # Increment the merged books counter
            merged_books += 1

        # Remove old author and name values
        g.remove((existing_book, ns1.author, None))
        g.remove((existing_book, ns1.name, None))

        # Add original author and name values
        g.add((existing_book, ns1.author, original_author))
        g.add((existing_book, ns1.name, original_name))

remove_duplicate_attributes(g)

print(f'Merged {merged_books} books.')

# Save the merged graph
g.serialize(destination='final_output.ttl', format='turtle')

from rdflib import Graph, Namespace
from difflib import SequenceMatcher
from rdflib import Literal
import csv

def best_matching_award(award, award_list):
    best_match = award
    best_ratio = 0
    award_lower = award.lower()

    for candidate in award_list:
        candidate_lower = candidate.lower()
        ratio = SequenceMatcher(None, award_lower, candidate_lower).ratio()
        if ratio > best_ratio:
            best_match = candidate
            best_ratio = ratio

    return best_match

# Define the namespace
ns1 = Namespace("http://schema.org/")

# Load the list of awards from the CSV file
with open('./awards.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    award_list = [row[0] for row in reader]  # Assuming one award per line

# List of TTL files to process
# filepaths = [
#     "./output-bookcentre.ttl",
#     "./output-fmdoc.ttl",
#     "./output-lurelu-tables.ttl",
#     "./output-lurelu.ttl",
#     "./output-prixdeslibraires-bd.ttl",
#     "./output-prixdeslibraires-essai.ttl",
#     "./output-prixdeslibraires-jeunesse.ttl",
#     "./output-prixdeslibraires-poesie.ttl",
#     "./output-prixdeslibraires-roman.ttl",
#     "./output-ricochet-tables.ttl",
#     "./output-ricochet.ttl",
# ]

filepaths =[
    "./output-ricochet-tables-2.ttl"
]

for filepath in filepaths:
    # Parse the ttl files
    g = Graph()
    g.parse(filepath, format="n3")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["award"]))

    for book in books:
        # Extract the current award
        award = str(g.value(subject=book, predicate=ns1["award"]))

        # Find the best matching award in the list
        best_match = best_matching_award(award, award_list)

        # Update the book's award in the graph
        g.set((book, ns1["award"], Literal(best_match)))

    output_data = g.serialize(format="turtle")

    # Write the updated data back to the TTL file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_data)

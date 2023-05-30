from difflib import SequenceMatcher
from collections import defaultdict
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from unidecode import unidecode

# Load the main data graph
g_main = Graph()
g_main.parse("./updated_output.ttl", format="turtle")

ns1 = Namespace("http://schema.org/")

# Function to group similar book names
def group_similar_books(g_main, tolerance=1):
    book_names = [str(name) for s, p, name in g_main.triples((None, ns1.name, None)) if str(name).strip()]
    book_names_lower = [unidecode(name.lower()) for name in book_names]
    groups = defaultdict(list)
    
    # Mapping of lower case unaccented name to original names
    book_mapping = defaultdict(list)
    for book_lower, book in zip(book_names_lower, book_names):
        book_mapping[book_lower].append(book)

    for i, book1 in enumerate(book_names_lower):
        for book2 in book_names_lower[i+1:]:
            if len(book1) > 0 and SequenceMatcher(None, book1, book2).ratio() >= 1 - tolerance/len(book1):
                for original_book1 in book_mapping[book1]:
                    groups[original_book1].extend(book_mapping[book2])

    return groups

# Group similar book names
similar_books = group_similar_books(g_main)

# Print the groups
for book, similar in similar_books.items():
    if similar:
        print(f"{book} is similar to: {', '.join(similar)}")


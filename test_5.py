from rdflib import Graph, Namespace, URIRef

# Define your namespaces
ns1 = Namespace("http://schema.org/")
mcc = Namespace("http://example.com/mcc#")  

# Load your graphs
books = Graph()
awards = Graph()

books.parse("./books.ttl", format="turtle")
awards.parse("./awards.ttl", format="turtle")

# Count the awards for each book in the books graph
book_awards_counts = {}
for s, p, o in books:
    if p == ns1["award"]:
        if s in book_awards_counts:
            book_awards_counts[s] += 1
        else:
            book_awards_counts[s] = 1

# Count the awards for each book in the awards graph
award_book_counts = {}
for s, p, o in awards:
    if p == mcc["R37"]:
        if o in award_book_counts:
            award_book_counts[o] += 1
        else:
            award_book_counts[o] = 1

# Compare the counts
for book, count in book_awards_counts.items():
    if book in award_book_counts:
        if count != award_book_counts[book]:
            print(f"The book {book} has different award counts in the two graphs.")
    else:
        print(f"The book {book} is not present in the awards graph.")



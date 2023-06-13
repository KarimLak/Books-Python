from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import XSD

# Define your namespaces
ns1 = Namespace("http://schema.org/")
mcc = Namespace("http://example.com/mcc#")
schema = Namespace("http://schema.org/")
pbs = Namespace("http://example.com/pbs#")

# Load your graphs
books = Graph()
books.parse("./books.ttl", format="ttl")

awards = Graph()
awards.parse("./awards.ttl", format="ttl")

# Create dictionaries for storing the books URIs
genre_to_books = {
    "Album": [],
    "Petit roman illustré": [],
    "Bande dessinée": [],
    "Relève": [],
}

# Iterate over the books and add the book URI to the corresponding genre list
for s, p, o in books.triples((None, ns1.award, None)):
    if "ustration_Jeunesse_Salon_Du_Livre_De_Trois_Rivi" in str(o):
        for genre in genre_to_books.keys():
            book_genres = [str(o) for o in books.objects(s, ns1.genre)]
            if genre in book_genres:
                genre_to_books[genre].append(str(s))

# Now genre_to_books dictionary contains the book URIs categorized by genre
# Create a dictionary to store award URIs instead of book URIs
genre_to_awards = {genre: [] for genre in genre_to_books.keys()}

# Iterate over the awards and replace the book URIs with the award URIs
for genre, book_uris in genre_to_books.items():
    for book_uri in book_uris:
        for s, p, o in awards.triples((None, mcc.R37, URIRef(book_uri))):
            genre_to_awards[genre].append(str(s))

# Now genre_to_awards dictionary contains the award URIs categorized by genre
# Now genre_to_awards dictionary contains the award URIs categorized by genre
for genre, awards in genre_to_awards.items():
    print(f"Genre: {genre}")
    # Inside your loop
    for award in awards:
        # Convert the URI to the preferred format
        award_formatted = award.replace('http://schema.org/', 'ns1:')
        print(f"{award_formatted},")
    print("\n")


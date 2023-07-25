from rdflib import Graph, Literal, URIRef
from bs4 import BeautifulSoup
import requests
import re
import concurrent.futures

# Define the namespace and predicates
ns1 = 'http://schema.org/'
author_pred = URIRef(f'{ns1}author')
bnfLink_pred = URIRef(f'{ns1}bnfLink')

# Load the .ttl file into an RDF graph
g = Graph()
g.parse("output_bnf_1.ttl", format="turtle")

# Load the already updated books
g_already_updated = Graph()
g_already_updated.parse("output_bnf_1_updated.ttl", format="turtle")

# Create a new RDF graph for the updated books
g_updated = Graph()

# Create a set of subjects from the updated graph
updated_subjects = set(g_already_updated.subjects())

# The number of operations after which to save the data
save_every = 10
operation_count = 0

# Prepare a list of books and their associated URLs, excluding already updated books
books_urls = [(subj, str(obj)) for subj, pred, obj in g if pred == bnfLink_pred and subj not in updated_subjects]

# Define a function to fetch the URL and return the response along with the associated book
def fetch(book, url):
    response = requests.get(url)
    return book, response

# Use a ThreadPoolExecutor to fetch the URLs in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(fetch, book, url): url for book, url in books_urls}
    for future in concurrent.futures.as_completed(future_to_url):
        book, response = future.result()
        soup = BeautifulSoup(response.content, 'html.parser')
        author_paragraph = soup.find('p', {'id': 'auteur'})

        if author_paragraph:
            author_links = author_paragraph.find_all('a')
            if len(author_links) >= 2:
                authors = []
                for author_link in author_links:
                    # Extract the name, remove the birth year and additional text
                    name = re.sub(r'\(.*?\)', '', author_link.text).strip()
                    # Skip the "Voir les notices liées en tant qu'auteur" text
                    if name != "Voir les notices liées en tant qu'auteur":
                        # Reverse the order of the names
                        names = name.split(',', 1)
                        if len(names) == 2:
                            last, first = names
                            authors.append(f"{first.strip()} {last.strip()}")
                        else:
                            authors.append(name)

                # Add the updated book to the new graph
                for pred, obj in g.predicate_objects(book):
                    if pred == author_pred:
                        # Add the new ns1:author attributes
                        for author in authors:
                            g_updated.add((book, pred, Literal(author)))
                    else:
                        g_updated.add((book, pred, obj))

        # Increment the operation counter and check if it's time to save
        operation_count += 1
        if operation_count % save_every == 0:
            g_updated.serialize("output_bnf_2_updated.ttl", format="turtle")
            print(f"Saved data after {operation_count} operations")

# Save the remaining changes
g_updated.serialize("output_bnf_2_updated.ttl", format="turtle")
print("Finished updating authors")
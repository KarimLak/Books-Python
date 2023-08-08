from difflib import SequenceMatcher
import time
import uuid
from bs4 import BeautifulSoup
from rdflib import XSD, Graph, Literal, BNode, Namespace, RDF, URIRef

ns1 = Namespace('http://schema.org/')

def remove_specific_words(string):
    words_to_remove = ['books', 'press', 'editions', 'editeur', 'éditeur', 'éditions', 'publishing', 'poche', 'jeunesse', 'publishers', 'publisher', ']', '[', 'éd.', 'ed.', 'ed', 'éd', 'roman', 'romans', 'les éditions de la', 'les éditions', 'de la', 'de', 'la', 'le', 'pocket', '!', '|', "l'"]
    for word in words_to_remove:
        string = string.lower().replace(word, '')
    return string

def get_publishers(graph):
    publishers_dict = {}
    for publisher in graph.subjects(RDF.type, ns1.Publisher):
        publisher_name = graph.value(publisher, ns1.name)
        if publisher_name:
            publishers_dict[str(publisher_name.lower())] = publisher
    return publishers_dict

publishers_graph = Graph()
publishers_graph.parse("./publishers.ttl", format='turtle')
publishers_dict = get_publishers(publishers_graph)

def get_existing_titles(graph):
    titles = []
    for s, p, o in graph.triples((None, ns1['name'], None)):
        titles.append(str(o).lower())
    return titles

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

existing_graph = Graph()
existing_graph.parse("./output_bnf.ttl", format='turtle')

def match_and_replace_publishers(existing_graph, publishers_dict):
    for book in existing_graph.subjects(RDF.type, ns1.Book):
        # Get the publisher's name for this book
        publisher_name = existing_graph.value(book, ns1.publisher)

        if publisher_name:
            publisher_name = str(publisher_name).lower()

            # Try to find a match in the existing publishers
            best_match = None
            best_ratio = 0

            for publisher, publisher_uri in publishers_dict.items():
                ratio = similar(publisher_name, publisher)

                if ratio > best_ratio:
                    best_match = publisher_uri
                    best_ratio = ratio

                # If we have a match that is better than 0.85, use it
                if best_ratio > 0.85:
                    existing_graph.set((book, ns1.publisher, URIRef(best_match)))
                    break
            else:
                # If we did not find a good match, remove specific words and try again
                publisher_name_modified = remove_specific_words(publisher_name)
                for publisher, publisher_uri in publishers_dict.items():
                    ratio = similar(publisher_name_modified, publisher)
                    if ratio > best_ratio:
                        best_match = publisher_uri
                        best_ratio = ratio

                    if best_ratio > 0.85:
                        existing_graph.set((book, ns1.publisher, URIRef(best_match)))
                        break
    return existing_graph


# Use the function
existing_graph = match_and_replace_publishers(existing_graph, publishers_dict)

# Save the updated graph
existing_graph.serialize("output_bnf_2_updated.ttl", format='turtle')
print("Finished updating publishers")

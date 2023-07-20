from bs4 import BeautifulSoup
import requests
import rdflib

# Load the original graph
original_graph = rdflib.Graph()
original_graph.parse('output_bnf_1.ttl', format='turtle')

# Create a new graph for storing treated books
treated_graph = rdflib.Graph()

# Query the original graph to find all books and their BNF links
qres = original_graph.query(
    """
    PREFIX schema1: <http://schema.org/>
    SELECT ?book ?bnfLink
    WHERE {
        ?book a schema1:Book .
        ?book schema1:bnfLink ?bnfLink .
    }
    """)

start_adding = False
for row in qres:
    book, bnfLink = row

    response = requests.get(bnfLink)
    soup = BeautifulSoup(response.text, 'html.parser')
    notice = soup.find('p', {'id': 'avisCnlj'})
    if notice is not None:
        lines = notice.text.split('\n')
        for line in lines:
            if 'Public destinataire' in line:
                publicDestinatairePrio = line.split(':')[1].strip()
                # Add the book and its properties to the treated graph
                for p, o in original_graph.predicate_objects(subject=book):
                    treated_graph.add((book, p, o))
                # Add the new property to the treated graph
                treated_graph.add((book, rdflib.Namespace('http://schema.org/')['publicDestinatairePrio'], rdflib.Literal(publicDestinatairePrio)))
                # Save the updated graph after processing each book
                treated_graph.serialize(destination='output_bnf_1_updated.ttl', format='turtle')

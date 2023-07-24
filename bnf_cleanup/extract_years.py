from bs4 import BeautifulSoup
import requests
from requests_futures.sessions import FuturesSession
import rdflib
import itertools
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Load the original graph
original_graph = rdflib.Graph()
original_graph.parse('output_bnf_2.ttl', format='turtle')

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

# Create a session that will perform 5 requests in parallel
session = FuturesSession(max_workers=5)

# Configure retries
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
adapter = HTTPAdapter(max_retries=retries)

# Add the adapter to the session
session.mount('http://', adapter)
session.mount('https://', adapter)

# Convert the result of the query into a list
qres_list = list(qres)

# Find the index of the book you want to start from
start_book_url = "http://catalogue.bnf.fr/ark:/12148/cb37315068w"
start_index = next(i for i, v in enumerate(qres_list) if str(v[1]) == start_book_url)

# Create a list of futures starting from the start index
futures = [(book, session.get(str(bnfLink))) for book, bnfLink in qres_list[start_index:]]

# Batch size for writing to disk
batch_size = 100
batches = itertools.zip_longest(*[iter(futures)]*batch_size, fillvalue=None)

for batch in batches:
    for future in batch:
        if future is not None:
            book, future_response = future
            response = future_response.result()
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

    # Save the updated graph after processing each batch
    treated_graph.serialize(destination='output_bnf_2_updated_2.ttl', format='turtle')

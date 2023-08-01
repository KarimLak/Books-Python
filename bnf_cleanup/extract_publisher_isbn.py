from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from requests_cache import CachedSession
from rdflib import Graph, Namespace, Literal
from time import sleep
import concurrent.futures
import math

ns1 = Namespace("http://schema.org/")
g = Graph()

g.parse("output_bnf_updated.ttl", format="turtle")
print('parsed')

session = CachedSession('book_cache', expire_after=3600)  # Cache will last for an hour

def process_book(book_url):
    for _ in range(5):  # retry up to 5 times
        try:
            response = session.get(book_url, timeout=10)

            soup = BeautifulSoup(response.text, 'html.parser')

            publisher_tag = soup.find('p', {'id': 'publication'})
            ean_tag = soup.find('p', {'id': 'numeros'})
            book_info = {}

            if publisher_tag:
                publisher_elements = publisher_tag.find_all('span')
                if len(publisher_elements) > 1:
                    publisher_text = publisher_elements[1].text
                    if publisher_text:
                        publisher_parts = publisher_text.strip().split(":")
                        if len(publisher_parts) > 1:
                            book_info['publisher'] = publisher_parts[1].split(",")[0].strip()
                            if 'ean' in book_info:  # Early exit if both publisher and EAN found
                                return book_info

            if ean_tag:
                ean_elements = ean_tag.find_all('span')
                if ean_elements:
                    for ean_text in ean_elements:
                        if "EAN" in ean_text.text:
                            book_info['ean'] = ean_text.text.strip().split("EAN ")[1].strip()
                            if 'publisher' in book_info:  # Early exit if both publisher and EAN found
                                return book_info

            return book_info

        except RequestException as e:
            print(f"Error while fetching '{book_url}': {e}")
            sleep(1)  # wait for a second before trying again

    return {}  # return an empty dict if all attempts fail

book_urls = [str(o) for s, p, o in g.triples((None, ns1.bnfLink, None))]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  
    results = list(executor.map(process_book, book_urls))

for i, (s, p, o) in enumerate(g.triples((None, ns1.bnfLink, None))):
    if 'publisher' in results[i]:
        g.set((s, ns1.publisher, Literal(results[i]['publisher'])))

    if 'ean' in results[i]:
        g.set((s, ns1.isbn, Literal(results[i]['ean'])))

    if i > 0 and i % 1000 == 0:  
        print(f"Processed {i} books")
        g.serialize(destination=f'output_bnf_updated_backup_{math.floor(i/1000)}.ttl', format='turtle')

g.serialize(destination='output_bnf_updated_new.ttl', format='turtle')

from bs4 import BeautifulSoup
import requests
import rdflib

url = 'https://www.lurelu.net/coupsdecoeur06.html#45_2_2022'
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')
book_rows = soup.find_all('tr')

graph = rdflib.Graph()
ns1 = rdflib.Namespace('http://schema.org/')
graph.bind('ns1', ns1)

for i, book_row in enumerate(book_rows):
    detail_td = book_row.find_all('td')[-1]
    p_tags = detail_td.find_all('p')

    if len(p_tags) > 0:  # Check if there are paragraph tags
        detail_strong = p_tags[0].find('strong')
        if detail_strong is not None:
            details = detail_strong.get_text(strip=True).rsplit(', ', 2)
            if len(details) == 3:
                author, title, publisher_date = details
            else:
                continue  # skip this book row because it doesn't have all the necessary fields

            # Split publisher_date into publisher and date_published, if possible
            if ' ' in publisher_date:
                publisher, date_published = publisher_date.rsplit(' ', 1)
            else:
                publisher = publisher_date
                date_published = ''

            # Replace spaces with underscores in publisher
            publisher = publisher.replace(' ', '_')

            resume = p_tags[1].get_text(strip=True)
            erudit_link = "https://www.erudit.org/fr/revues/lurelu/2018-v41-n2-lurelu03960/88789ac/"  # Placeholder value

            book_id = f"Book{i}"
            book = ns1.term(book_id)
            graph.add((book, rdflib.RDF.type, ns1.Book))
            graph.add((book, ns1.auteur, rdflib.Literal(author)))
            graph.add((book, ns1.name, rdflib.Literal(publisher)))  # Swapping publisher and name
            graph.add((book, ns1.publisher, ns1.term(title.replace(' ', '_'))))  # Swapping publisher and name
            graph.add((book, ns1.resume, rdflib.Literal(resume)))
            graph.add((book, ns1.lureluLink, rdflib.Literal(url)))
            graph.add((book, ns1.eruditLink, rdflib.Literal(erudit_link)))
            if date_published != '':
                graph.add((book, ns1.datePublished, rdflib.Literal(date_published, datatype=rdflib.namespace.XSD.gYear)))
            graph.add((book, ns1.language, rdflib.Literal("Français")))

graph.serialize(destination='output_lurelu_2.ttl', format='turtle')

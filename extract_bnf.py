import csv
import requests
from bs4 import BeautifulSoup, NavigableString

turtle_template = """
ns1:Book{id} a ns1:Book ;
    ns1:bnfLink "{bnfLink}" ;
    ns1:isbn "{isbn}" ;
    ns1:author "{author}" ;
    ns1:publisher "{publisher}" ;
    ns1:datePublished "{datePublished}"^^xsd:gYear ;
    ns1:title "{title}" ;
    ns1:description "{description}" ;
    ns1:language "{language}" ;
    ns1:format "{format}" ;
    ns1:publicDestinataire "{publicDestinataire}" ;
    ns1:resume "{resume}" ;
    ns1:genre "{genre}" ;
    ns1:avisCritique "{avisCritique}" ;
    ns1:noticeCritique "{noticeCritique}" .
"""

def get_book_data(bnfLink):
    response = requests.get(bnfLink)
    soup = BeautifulSoup(response.text, 'html.parser')

    publicDestinataire_element = soup.find(id='publicCnlj')
    publicDestinataire = publicDestinataire_element.get_text(strip=True).split(':', 1)[-1] if publicDestinataire_element else ""

    resume_element = soup.find(id='resumeCnlj')
    resume = resume_element.get_text(strip=True).split(':', 1)[-1] if resume_element else ""

    avisCnlj_content = soup.find(id='avisCnlj')

    avisCnlj_lines = avisCnlj_content.stripped_strings if avisCnlj_content else []

    data = {}
    for line in avisCnlj_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()

    genre = data.get("Genre", "")
    avis_critique = data.get("Avis critique", "")
    notice_critique = data.get("Notice critique", "")

    return publicDestinataire, resume, genre, avis_critique, notice_critique


def csv_to_turtle(csv_file, output_file):
    with open(csv_file, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        with open(output_file, 'w', encoding='utf-8') as out:
            next(reader, None)  # skip the headers
            for row in reader:
                id = row[1]
                bnf_isbn = row[0].split(" | ")
                bnfLink = bnf_isbn[0]
                isbn = bnf_isbn[1] if len(bnf_isbn) > 1 else ""
                author = row[5]
                publisher = row[7]
                datePublished = row[8]
                title = row[4]
                description = row[9]
                language = row[11]
                format = row[12]
                publicDestinataire, resume, genre, avisCritique, noticeCritique = get_book_data(bnfLink)

                out.write(turtle_template.format(id=id, bnfLink=bnfLink, isbn=isbn, author=author, publisher=publisher, datePublished=datePublished, title=title, description=description, language=language, format=format, publicDestinataire=publicDestinataire, resume=resume, genre=genre, avisCritique=avisCritique, noticeCritique=noticeCritique))

csv_to_turtle('./export_public.csv', './output_2.ttl')

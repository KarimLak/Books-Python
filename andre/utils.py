import rdflib
import unicodedata
import re

EPSILON = 0.00001

def create_key(book_name, book_author="", publisher="", publication_date=""):
    return book_name + "_" + book_author + "_" + publisher + "_" + publication_date


pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")

class RdfBookData:
    def __init__(self, book_name, book_author, age_range_int, url, publication_date, publisher, isbn):
        self.book_name = book_name
        self.book_author = book_author
        self.age_range_int = age_range_int
        self.url = url
        self.publication_date = publication_date
        self.publisher = publisher
        self.isbn = isbn

def extract_data_constellation(graph, book):
    book_name = str(graph.value(book, ns1.name)) if str(graph.value(book, ns1.name)) else str(
        graph.value(book, ns1.title))  # name vs title in database
    book_author = str(graph.value(book, ns1.author))
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, pbs.constellationLink))
    publication_date = str(graph.value(book, pbs.dateEdition))
    publisher = str(graph.value(book, ns1.publisher))
    isbn = str(graph.value(book, ns1.isbn))
    return RdfBookData(book_name=book_name, book_author=book_author, age_range_int=age_range_int, url=url, publication_date=publication_date, publisher=publisher, isbn=isbn)

def extract_data_bnf(graph, book):
    book_name = str(graph.value(book, ns1.name))
    book_author = str(graph.value(book, ns1.author))
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, pbs.bnfLink)) if graph.value(book, pbs.bnfLink) else str(graph.value(book, ns1.bnfLink)) #4 august vs 8 august data
    publication_date = str(graph.value(book, ns1.datePublished))
    publisher = str(graph.value(book, ns1.publisher))
    isbn = str(graph.value(book, ns1.isbn))
    return RdfBookData(book_name=book_name, book_author=book_author, age_range_int=age_range_int, url=url, publication_date=publication_date, publisher=publisher, isbn=isbn)

def extract_data_lurelu(graph, book):
    book_name = str(graph.value(book, ns1.name))
    book_author = str(graph.value(book, ns1.author))
    url = str(graph.value(book, ns1.lureluLink))
    publication_date = str(graph.value(book, ns1.datePublished))
    publisher = str(graph.value(book, ns1.publisher))
    isbn = str(graph.value(book, ns1.isbn)) if graph.value(book, ns1.isbn) else ""
    return RdfBookData(book_name=book_name, book_author=book_author, url=url,
                       publication_date=publication_date, publisher=publisher, isbn=isbn, age_range_int=None)
def remove_spaces(book_data: RdfBookData):
    book_data.book_name = book_data.book_name.replace(" ", "")
    book_data.book_author = book_data.book_author.replace(" ", "")
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = book_data.publication_date.replace(" ", "")
    book_data.publisher = book_data.publisher.replace(" ", "")
    book_data.isbn = book_data.isbn.replace(" ", "")
    return book_data

def lower(book_data: RdfBookData):
    book_data.book_name = book_data.book_name.lower()
    book_data.book_author = book_data.book_author.lower()
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = book_data.publication_date.lower()
    book_data.publisher = book_data.publisher.lower()
    book_data.isbn = book_data.isbn.lower()
    return book_data
def strip_special_chars(s):
    return re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,']", "", s) # also remove []

def remove_special_chars(book_data: RdfBookData):
    book_data.book_name = strip_special_chars(book_data.book_name)
    book_data.book_author = strip_special_chars(book_data.book_author)
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = strip_special_chars(book_data.publication_date)
    book_data.publisher = re.sub(r"h.*/","", book_data.publisher) # removes the http://schema.org/ prefix
    book_data.isbn = strip_special_chars(book_data.isbn)
    return book_data

def remove_accents(book_data: RdfBookData):
    book_data.book_name = strip_accents(book_data.book_name)
    book_data.book_author = strip_accents(book_data.book_author)
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = strip_accents(book_data.publication_date)
    book_data.publisher = strip_accents(book_data.publisher)
    book_data.isbn = strip_accents(book_data.isbn)
    return book_data
def strip_accents(text):
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

def jaccard(list1, list2):
    # Find the number of common elements in both lists
    common_elements = set(list1).intersection(set(list2))
    num_common_elements = len(common_elements)

    # Find the total number of unique elements in both lists
    total_elements = set(list1).union(set(list2))
    num_total_elements = len(total_elements)

    if total_elements:
        percentage_similarity = (num_common_elements / (num_total_elements)) * 100
    else:
        percentage_similarity = 0

    return percentage_similarity

import rdflib
import unicodedata
import re
import logging
from difflib import SequenceMatcher
import os

EPSILON = 0.00001

pbs = rdflib.namespace.Namespace("http://www.example.org/pbs#")
schema = rdflib.namespace.Namespace("http://schema.org/")
btlf_classe = rdflib.namespace.Namespace("http://www.btlf.com/classe/")
btlf_livre = rdflib.namespace.Namespace("http://www.btlf.com/livre/")
xsd = rdflib.namespace.Namespace('http://www.w3.org/2001/XMLSchema#')


def preprocess_publisher_name(raw_name):
    preprocessed_name = raw_name
    preprocessed_name = preprocessed_name.replace(" SARL", "")
    preprocessed_name = preprocessed_name.replace("&#233;", "e")
    preprocessed_name = preprocessed_name.replace(" SA", "")
    preprocessed_name = preprocessed_name.replace("Ed. ", "")
    preprocessed_name = preprocessed_name.replace(" éd.", "")
    preprocessed_name = preprocessed_name.lower()
    preprocessed_name = preprocessed_name.replace("et cie", "")
    preprocessed_name = preprocessed_name.replace("& cie", "")
    preprocessed_name = strip_special_chars(preprocessed_name)
    preprocessed_name = strip_accents(preprocessed_name)
    preprocessed_name = preprocessed_name.replace("librairies", "")
    preprocessed_name = preprocessed_name.replace("librairie", "")
    preprocessed_name = preprocessed_name.replace("editeurs", "")
    preprocessed_name = preprocessed_name.replace("editeur", "")
    preprocessed_name = preprocessed_name.replace("les editions", "")
    preprocessed_name = preprocessed_name.replace("editions", "")
    preprocessed_name = preprocessed_name.replace("edition", "")
    preprocessed_name = preprocessed_name.replace(" ", "")
    preprocessed_name = preprocessed_name.replace("groupe", "")
    preprocessed_name = preprocessed_name.strip()

    return raw_name if not preprocessed_name else preprocessed_name

def preprocess_author_name(raw_name):
    preprocessed_name = raw_name
    preprocessed_name = preprocessed_name.lower()
    preprocessed_name = strip_special_chars(preprocessed_name)
    preprocessed_name = strip_accents(preprocessed_name)
    preprocessed_name = preprocessed_name.strip()

    return raw_name if not preprocessed_name else preprocessed_name

class Publisher:
    def __init__(self, source, uri, raw_name, preprocessed_name):
        self.source = source
        self.uri = uri  
        self.raw_name = raw_name  
        self.preprocessed_name = preprocessed_name  

    def __str__(self):
      return f"uri = {self.uri}, \n  source = {self.source},\n  raw_name = {self.raw_name},\n  preprocessed_name = {self.preprocessed_name}"

def create_key(book_name, book_author:list=[], publisher="", publication_date=""):
    authors_string = ""
    if len(book_author) > 1 and len(book_author[0]) > 1: # eviter que le book author soit juste 1 auteur et qu'on mette des '+' entre chaque caractere
        for a in book_author:
            authors_string += a
            authors_string += "+"
        if authors_string[-1] == "+":
            authors_string = authors_string[:-1]
    elif len(book_author) == 1:
        authors_string = book_author[0]
    elif len(book_author) == 0:
        authors_string = ""
    else:
        print("author key creation edge case")
    return book_name + "_" + authors_string + "_" + publisher + "_" + publication_date


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def delete_empty_logfile(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()
        if os.path.getsize(handler.baseFilename) == 0:
            os.remove(handler.baseFilename)

def is_key_close_enough_to_another_key(book_key, keys_to_check, SIMILARITY_RATIO):
    max_ratio = 0
    best_key = ""
    for key_to_check in keys_to_check:
        s = SequenceMatcher(None, book_key, key_to_check)
        ratio = s.ratio()
        if ratio >= SIMILARITY_RATIO and ratio > max_ratio:
            best_key = key_to_check
            max_ratio = ratio
    return best_key, max_ratio


class RdfBookData:
    def __init__(self, uri, book_name=None, book_authors=None, age_range_int=None, url=None,
                  publication_date=None, publisher=None, isbn=None, ean=None, language=None, illustrator = None):
        self.book_name = book_name
        self.book_authors = book_authors
        self.age_range_int = age_range_int
        self.url = url
        self.publication_date = publication_date
        self.publisher = publisher
        self.isbn = isbn
        self.uri = uri
        self.ean = ean
        self.language = language
        self.illustrator = illustrator


def extract_data_alignment(graph, alignment_uri):
    isbn = graph.value(alignment_uri, schema.isbn)
    exact_key = graph.value(alignment_uri, pbs.exact_key)
    name = graph.value(alignment_uri, schema.name)
    author = graph.value(alignment_uri, schema.author)
    datePublished = graph.value(alignment_uri, schema.datePublished)
    uri_constellation = graph.value(alignment_uri, pbs.uri_constellation) if graph.value(alignment_uri,
                                                                                         pbs.uri_constellation) else None
    uri_bnf = graph.value(alignment_uri, pbs.uri_bnf) if graph.value(alignment_uri, pbs.uri_bnf) else None
    uri_lurelu = graph.value(alignment_uri, pbs.uri_lurelu) if graph.value(alignment_uri, pbs.uri_lurelu) else None
    return isbn, exact_key, name, author, datePublished, uri_constellation, uri_bnf, uri_lurelu


def extract_data_constellation(graph, book):
    book_name = str(graph.value(book, schema.name)) if graph.value(book, schema.name) else str(
        graph.value(book, schema.title))  # name vs title in database
    book_authors = list(graph.objects(book, pbs.authorString))
    illustrator = str(graph.value(book, schema.illustrator)) if graph.value(book, schema.illustrator) else ""
    book_authors_str = [str(a) for a in book_authors]
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, pbs.constellationLink))
    publication_date = str(graph.value(book, pbs.dateEdition))
    publisher = str(graph.value(book, schema.publisher))
    isbn = str(graph.value(book, schema.isbn)) if (graph.value(book, schema.isbn) and str(graph.value(book, schema.isbn)) != "none") else ""
    uri = book
    return RdfBookData(book_name=book_name, book_authors=book_authors_str, age_range_int=age_range_int, url=url,
                       publication_date=publication_date, publisher=publisher, isbn=isbn, uri=uri, illustrator=illustrator)

# no url for btlf data
def extract_data_btlf(graph, book):
    book_name = str(graph.value(book, schema.name)) if graph.value(book, schema.name) else ""
    # book_author = str(graph.value(book, pbs.authorString)) if graph.value(book, pbs.authorString) else ""
    book_authors = list(graph.objects(book, pbs.authorString))
    book_authors_str = [str(a) for a in book_authors]
    age_range = list(graph.objects(book, pbs.age))
    age_range_int = [int(age) for age in age_range]
    publication_date = str(graph.value(book, schema.datePublished))
    publisher = str(graph.value(book, schema.publisher))
    illustrator = str(graph.value(book, pbs.illustratorString)) if graph.value(book, pbs.illustratorString) else ""
    # if not book_author:
    #     book_author = illustrator
    isbn = str(graph.value(book, schema.isbn)) if (graph.value(book, schema.isbn) and str(graph.value(book, schema.isbn)) != "none") else ""
    uri = book
    return RdfBookData(book_name=book_name, book_authors=book_authors_str, age_range_int=age_range_int,
                       publication_date=publication_date, publisher=publisher, isbn=isbn, uri=uri, url = uri, illustrator = illustrator)


def extract_data_bnf(graph, book):
    book_name = str(graph.value(book, schema.name)) if graph.value(book, schema.name) else ""
    language = str(graph.value(book, schema.inLanguage)) if graph.value(book, schema.inLanguage) else ""
    book_authors = list(graph.objects(book, pbs.authorString))
    book_authors_str = [str(a) for a in book_authors]
    illustrator = str(graph.value(book, schema.illustrator)) if graph.value(book, schema.illustrator) else ""
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, pbs.bnfLink)) if graph.value(book, pbs.bnfLink) else str(
        graph.value(book, schema.bnfLink))  # 4 august vs 8 august data
    publication_date = str(graph.value(book, schema.datePublished)) if graph.value(book, schema.datePublished) else ""
    publisher = str(graph.value(book, schema.publisher)) if graph.value(book, schema.publisher) else ""
    isbn = str(graph.value(book, schema.isbn)) if (graph.value(book, schema.isbn) and str(graph.value(book, schema.isbn)) != "none") else ""
    ean = str(graph.value(book, pbs.ean)) if (graph.value(book, pbs.ean) and str(graph.value(book, pbs.ean)) != "none") else ""
    uri = book
    return RdfBookData(book_name=book_name, book_authors=book_authors_str, age_range_int=age_range_int, url=url,
                       publication_date=publication_date, publisher=publisher, isbn=isbn, uri=uri, ean=ean, language=language, illustrator=illustrator)


def extract_data_babelio(graph, book):
    book_name = str(graph.value(book, schema.name)) if graph.value(book, schema.name) else ""
    language = str(graph.value(book, schema.inLanguage)) if graph.value(book, schema.inLanguage) else ""
    book_authors = list(graph.objects(book, schema.author))
    book_authors_str = [str(a) for a in book_authors]
    illustrator = str(graph.value(book, schema.illustrator)) if graph.value(book, schema.illustrator) else ""
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    publication_date = str(graph.value(book, schema.datePublished)) if graph.value(book, schema.datePublished) else ""
    publisher = str(graph.value(book, schema.publisher)) if graph.value(book, schema.publisher) else ""
    ean = str(graph.value(book, pbs.ean)) if (graph.value(book, pbs.ean) and str(graph.value(book, pbs.ean)) != "none") else ""
    uri = book
    return RdfBookData(book_name=book_name, book_authors=book_authors_str, age_range_int=age_range_int,
                       publication_date=publication_date, publisher=publisher, isbn=ean, uri=uri, url = uri, language=language, illustrator=illustrator) # only ean available

def extract_data_lurelu(graph, book):
    book_name = str(graph.value(book, schema.name))
    book_author = str(graph.value(book, schema.author)) if graph.value(book, schema.author) else ""
    url = str(graph.value(book, pbs.lureluLink))
    publication_date = str(graph.value(book, schema.datePublished)) if graph.value(book, schema.datePublished) else ""
    publisher = str(graph.value(book, schema.publisher)) if graph.value(book, schema.publisher) else ""
    isbn = str(graph.value(book, schema.isbn)) if (
            graph.value(book, schema.isbn) and str(graph.value(book, schema.isbn)) != "none") else ""
    uri = book
    return RdfBookData(book_name=book_name, book_authors=book_author, url=url,
                       publication_date=publication_date, publisher=publisher, isbn=isbn, age_range_int=None, uri=uri)


def remove_spaces(book_data: RdfBookData):
    book_data.book_name = book_data.book_name.replace(" ", "")
    book_data.book_authors = [a.replace(" ", "") for a in book_data.book_authors]
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = book_data.publication_date.replace(" ", "")
    book_data.publisher = book_data.publisher.replace(" ", "")
    book_data.isbn = book_data.isbn.replace(" ", "")
    return book_data


def lower(book_data: RdfBookData):
    book_data.book_name = book_data.book_name.lower()
    book_data.book_authors = [a.lower()for a in book_data.book_authors]
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = book_data.publication_date.lower()
    book_data.publisher = book_data.publisher.lower()
    book_data.isbn = book_data.isbn.lower()
    return book_data


def strip_special_chars(s):
    return re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,']", "", s)


def remove_special_chars(book_data: RdfBookData):
    book_data.book_name = strip_special_chars(book_data.book_name)
    book_data.book_authors = [strip_special_chars(a) for a in book_data.book_authors]
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = strip_special_chars(book_data.publication_date)
    book_data.publisher = re.sub(r"h.*/", "", book_data.publisher)  # removes the http://schema.org/ prefix
    book_data.isbn = strip_special_chars(book_data.isbn)
    return book_data


def remove_accents(book_data: RdfBookData):
    book_data.book_name = strip_accents(book_data.book_name)
    book_data.book_authors = [strip_accents(a) for a in book_data.book_authors]
    book_data.age_range_int = book_data.age_range_int
    book_data.url = book_data.url
    book_data.publication_date = strip_accents(book_data.publication_date)
    book_data.publisher = strip_accents(book_data.publisher)
    book_data.isbn = strip_accents(book_data.isbn)
    return book_data


def strip_accents(text):
    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
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

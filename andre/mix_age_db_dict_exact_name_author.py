from rdflib import Graph, Literal, BNode
from rdflib.namespace import RDF, FOAF, XSD
import rdflib.namespace
from difflib import SequenceMatcher
import csv
from cProfile import Profile
from pstats import SortKey, Stats

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


class BookAges:
    def __init__(self, book_name, author, age_range_constellation=None, age_range_bnf=None):
        self.book_name = book_name
        self.author = author
        self.age_range_constellation = age_range_constellation  # list not used to conserve source in db
        self.age_range_bnf = age_range_bnf

    def add_age_bnf(self, age_range):
        self.age_range_bnf = age_range

def create_key(book_name, book_author):
    return book_name + "_" + book_author

# load the graph of constellation
g = Graph()
g.parse("output_constellations.ttl", format="turtle")

list_of_BookAges = {}

# O(N)
for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.name))
    book_author = str(g.value(book, ns1.author))
    age_range = list(g.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    if age_range_int:
        key = create_key(book_name, book_author)
        list_of_BookAges[key] = BookAges(book_name=book_name, author= book_author, age_range_constellation=age_range_int)

# reset graph
g = Graph()
g.parse("output_bnf_1_updated.ttl", format="turtle")
# g.parse("output_bnf_2.ttl", format="turtle")


def find_book_in_list_of_BookAges_approximate_name(book_name, book_author, age_range): #O(1)
    key = create_key(book_name, book_author)
    if key in list_of_BookAges:
        list_of_BookAges[key].add_age_bnf(age_range)
    else:
        list_of_BookAges[key] = BookAges(book_name=book_name, author=book_author, age_range_bnf=age_range)


# 2 loops needed because age_range not normalized yet
for book in g.subjects(RDF.type, ns1.Book): #O(M)
    book_name = str(g.value(book, ns1.title))
    book_author = str(g.value(book, ns1.author))
    age_range = str(g.value(book, ns1.publicDestinatairePrio))
    if age_range:
        find_book_in_list_of_BookAges_approximate_name(book_name, book_author, age_range)


with open("output.csv", "w", encoding='utf-8', newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter='{')
    writer.writerow(["book_name", "book_author", "age_range_constellation", "age_range_bnf"])
    for bookAge in list_of_BookAges.values():
        writer.writerow([bookAge.book_name, bookAge.author, bookAge.age_range_constellation, bookAge.age_range_bnf])


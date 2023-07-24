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


# load the graph of constellation
g = Graph()
g.parse("output_constellation_updated_light.ttl", format="turtle")

list_of_BookAges = []

# O(N)
for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.name))
    book_author = str(g.value(book, ns1.author))
    age_range =  list(g.objects(book, ns1.ageRange))
    list_of_BookAges.append(BookAges(book_name=book_name, author= book_author, age_range_constellation=age_range))

# reset graph
g = Graph()
g.parse("output_bnf_1.ttl", format="turtle")
# g.parse("output_bnf_2.ttl", format="turtle")


# match by exact name   
# ---------------------------
# -> will not match if small error in book name 
# not complete because will not add a new book row if book is not found
def find_book_in_list_of_BookAges_exact_name(book_name, age_range):
    for bookAge in list_of_BookAges:
        if book_name == bookAge.book_name:
            bookAge.add_age_bnf(age_range)


# match by approximate name
# ---------------------------
# finds matching for Le jour des châteaux de sable
# problem: official name of book is trunkated (but not fault of function, cannot guess which source is wrong especially when it is our golden Constellation source)
def find_book_in_list_of_BookAges_approximate_name(book_name, book_author, age_range):
    bookIsFound = False
    for bookAge in list_of_BookAges: #O(N+M)
        s = SequenceMatcher(None, book_name, bookAge.book_name)
        if s.ratio() >= 0.9:
            bookAge.add_age_bnf(age_range)
            bookIsFound = True
    if not bookIsFound:
        list_of_BookAges.append(BookAges(book_name=book_name, author=book_author, age_range_bnf=age_range))


# 2 loops needed because age_range not normalized yet
# O(N+M) * O(M) = O(N^2 + M)
for book in g.subjects(RDF.type, ns1.Book): #O(M)
    book_name = str(g.value(book, ns1.title))
    book_author = str(g.value(book, ns1.author))
    age_range = str(g.value(book, ns1.publicDestinataire))
    find_book_in_list_of_BookAges_approximate_name(book_name, book_author, age_range)

# with open("output.csv", "w", newline="") as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(["book_name", "book_author", "age_range_constellation", "age_range_bnf"])
#     for bookAge in list_of_BookAges:
#         writer.writerow([bookAge.book_name, bookAge.author, bookAge.age_range_constellation, bookAge.age_range_bnf])

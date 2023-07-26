from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
import csv
from utils import create_key, extract_data_bnf, extract_data_constellation

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


class BookAlignment:
    def __init__(self, isbn_constellation=None, isbn_bnf=None, age_range_constellation=None,
                 age_range_bnf=None, url_constellation=None, url_bnf=None):
        self.isbn_constellation = isbn_constellation
        self.isbn_bnf = isbn_bnf
        self.age_range_constellation = age_range_constellation  # list not used to conserve source in db
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf
        self.url_constellation = url_constellation

    def align(self, isbn_bnf, age_range_bnf, url_bnf):
        self.isbn_bnf = isbn_bnf
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf


class InterDBStats:
    def __init__(self, key_type) -> None:
        self.total_book_number = 0
        self.constellation_book_number = 0
        self.bnf_book_number = 0
        self.number_of_alignments = 0
        self.collision_number = 0
        self.key_type = key_type

    def increment_alignment_number(self):
        self.number_of_alignments += 1

    def increment_collision_number(self):
        self.collision_number += 1

    def increment_bnf_book_number(self):
        self.bnf_book_number += 1

    def increment_constellation_book_number(self):
        self.constellation_book_number += 1

    def compute_alignment_accuracy(self, book_alignments):
        print("------------------------------------")
        print("key type", self.key_type)

        isbn_equality = 0
        isbn_inequality = 0
        missing_isbn_bnf = 0
        missing_isbn_constellation = 0
        for book in book_alignments:
            isbn_constellation = book_alignments[book].isbn_constellation
            isbn_bnf = book_alignments[book].isbn_bnf

            url_constellation = book_alignments[book].url_constellation
            url_bnf = book_alignments[book].url_bnf

            if url_bnf and url_constellation:  # proof of alignment because never missing

                if isbn_constellation and isbn_bnf:
                    if isbn_bnf == isbn_constellation:
                        isbn_equality += 1
                    else:
                        isbn_inequality += 1
                if not isbn_constellation:
                    missing_isbn_constellation += 1
                if isbn_constellation and not isbn_bnf:
                    missing_isbn_bnf += 1

        print("number of correct isbn matches", isbn_equality)
        print("number of incorrect isbn matches", isbn_inequality)
        print("missing isbn constellation", missing_isbn_constellation)
        print("missing isbn bnf", missing_isbn_bnf)
        print("proportion of correct isbn matches over total number of alignment",
              isbn_equality / self.number_of_alignments)
        print("proportion of incorrect isbn matches over total number of alignment",
              isbn_inequality / self.number_of_alignments)

    def print_stats(self):
        print("------------------------------------")
        print("key type", self.key_type)
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        print("number of alignments", self.number_of_alignments)
        print("total number of books", self.total_book_number)
        print("total number of books bnf", self.bnf_book_number)
        print("total number of books constellation", self.constellation_book_number)
        print("total number of collisions", self.collision_number)


name_author_book_alignments = {}
name_author_publisher_book_alignments = {}

stats_name_author = InterDBStats("name_author")
stats_name_author_publisher = InterDBStats("name_author_publisher")

# constellations
# ----------------------------------------------------


# load the graph of constellation
g = Graph()
g.parse("../output_constellations.ttl", format="turtle")

# constellation loop
for book in g.subjects(RDF.type, ns1.Book):
    book_name, book_author, age_range_int, url, publication_date, publisher, isbn = extract_data_constellation(g, book)
    stats_name_author.increment_constellation_book_number()
    stats_name_author_publisher.increment_constellation_book_number()

    book_alignment = BookAlignment(url_constellation=url,
                                   isbn_constellation=isbn,
                                   age_range_constellation=age_range_int)

    name_author_key = create_key(book_name, book_author)
    name_author_publisher_key = create_key(book_name, book_author, publisher)

    name_author_book_alignments[name_author_key] = book_alignment
    name_author_publisher_book_alignments[name_author_publisher_key] = book_alignment

# BNF
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_bnf_updated.ttl", format="turtle")


def alignment_by_name_author(book_ages, book_name, book_author):  # O(1)
    key = create_key(book_name, book_author)
    if key in name_author_book_alignments:
        if not name_author_book_alignments[key].url_bnf:  # not a collision
            name_author_book_alignments[key].align(isbn_bnf=book_ages.isbn_bnf,
                                                   age_range_bnf=book_ages.age_range_bnf,
                                                   url_bnf=book_ages.url_bnf)
            stats_name_author.increment_alignment_number()
        else:
            stats_name_author.increment_collision_number()


    else:
        name_author_book_alignments[key] = book_ages


def alignment_by_name_author_publisher(book_ages, book_name, book_author, book_publisher):  # O(1)
    key = create_key(book_name, book_author, book_publisher)
    if key in name_author_publisher_book_alignments:
        if not name_author_publisher_book_alignments[key].url_bnf:  # not a collision: bnf data not present
            name_author_publisher_book_alignments[key].align(isbn_bnf=book_ages.isbn_bnf,
                                                             age_range_bnf=book_ages.age_range_bnf,
                                                             url_bnf=book_ages.url_bnf)
            stats_name_author_publisher.increment_alignment_number()
        else:
            stats_name_author_publisher.increment_collision_number() # bnf data already present because of doublon name_author_publisher inside bnf; independant of alignement


    else:
        name_author_publisher_book_alignments[key] = book_ages # useful to add books that will not get a match ? -> good for collision stats


# BNF loop
for book in g.subjects(RDF.type, ns1.Book):  # O(M)
    book_name, book_author, age_range_int, url, publication_date, publisher, isbn = extract_data_bnf(g, book)
    book_alignment = BookAlignment(url_bnf=url,
                                   isbn_bnf=isbn,
                                   age_range_bnf=age_range_int)

    alignment_by_name_author(book_alignment, book_name, book_author)
    alignment_by_name_author_publisher(book_alignment, book_name, book_author, publisher)

    stats_name_author.increment_bnf_book_number()
    stats_name_author_publisher.increment_bnf_book_number()


with open("data/alignment_name_author.csv", "w", encoding='utf-8', newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter='{')
    writer.writerow(["key",
                     "isbn_constellation",
                     "isbn_bnf",
                     "age_range_constellation",
                     "age_range_bnf",
                     "url_constellation",
                     "url_bnf"])
    for key in name_author_book_alignments.keys():
        book_alignment = name_author_book_alignments[key]
        writer.writerow([key,
                         book_alignment.isbn_constellation,
                         book_alignment.isbn_bnf,
                         book_alignment.age_range_constellation,
                         book_alignment.age_range_bnf,
                         book_alignment.url_constellation,
                         book_alignment.url_bnf])


with open("data/alignment_name_author_publisher.csv", "w", encoding='utf-8', newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter='{')
    writer.writerow(["key",
                     "isbn_constellation",
                     "isbn_bnf",
                     "age_range_constellation",
                     "age_range_bnf",
                     "url_constellation",
                     "url_bnf"])
    for key in name_author_publisher_book_alignments.keys():
        book_alignment = name_author_publisher_book_alignments[key]
        writer.writerow([key,
                         book_alignment.isbn_constellation,
                         book_alignment.isbn_bnf,
                         book_alignment.age_range_constellation,
                         book_alignment.age_range_bnf,
                         book_alignment.url_constellation,
                         book_alignment.url_bnf])


stats_name_author.print_stats()
stats_name_author_publisher.print_stats()

stats_name_author.compute_alignment_accuracy(name_author_book_alignments)
stats_name_author_publisher.compute_alignment_accuracy(name_author_publisher_book_alignments)

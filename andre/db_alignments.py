import string

from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
import csv
import utils
import copy

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
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.bnf_book_number: int = 0
        self.alignments_number: int = 0
        self.collision_number: int = 0
        self.key_type: string = key_type
        self.all_book_alignments: dict[string, BookAlignment] = {}

    def increment_alignment_number(self):
        self.alignments_number += 1

    def increment_collision_number(self):
        self.collision_number += 1

    def increment_bnf_book_number(self):
        self.bnf_book_number += 1

    def increment_constellation_book_number(self):
        self.constellation_book_number += 1

    def  align_by_key(self, book_alignment, book_key):  # O(1)
        if book_key in self.all_book_alignments:
            if not self.all_book_alignments[book_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key].align(isbn_bnf=book_alignment.isbn_bnf,
                                                         age_range_bnf=book_alignment.age_range_bnf,
                                                         url_bnf=book_alignment.url_bnf)
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf


        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    def is_isbn_in_alignments_bnf(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "bnf")

    def is_isbn_in_alignments_constellation(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "constellation")

    def is_isbn_in_alignments(self, target_isbn, source) -> bool:
        if source == "bnf":
            for book in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book].isbn_bnf:
                    return True
        elif source =="constellation":
            for book in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book].isbn_constellation:
                    return True
        else:
            print(f"wrong source in is_isbn_in_alignments, {source} doesn't exist")
        return False

    def compute_alignment_confusion_matrix(self):

        print("-----")
        isbn_equality = 0 # TP
        isbn_inequality = 0 # FP
        missing_isbn_bnf = 0
        missing_isbn_constellation = 0
        total_non_alignment = 0 # N
        total_alignment = 0 # P
        non_alignment_isbn_present = 0 # FN
        non_alignment_isbn_absent = 0 # TN
        lines_without_url = 0
        for book_key in self.all_book_alignments:
            isbn_constellation = self.all_book_alignments[book_key].isbn_constellation
            isbn_bnf = self.all_book_alignments[book_key].isbn_bnf

            url_constellation = self.all_book_alignments[book_key].url_constellation
            url_bnf = self.all_book_alignments[book_key].url_bnf

            if url_bnf and url_constellation:  # proof of alignment because never missing
                total_alignment += 1
                if isbn_constellation and isbn_bnf:
                    if isbn_bnf == isbn_constellation:
                        isbn_equality += 1
                    else:
                        isbn_inequality += 1
                if not isbn_constellation:
                    missing_isbn_constellation += 1
                if not isbn_bnf:
                    missing_isbn_bnf += 1
            elif url_bnf and not url_constellation: # non-alignment: only 1 bnf present
                total_non_alignment += 1
                if isbn_bnf:
                    # look if isbn present in a constellation book
                    if self.is_isbn_in_alignments_constellation(isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent +=1
                else:
                    missing_isbn_bnf += 1
            elif not url_bnf and url_constellation:
                total_non_alignment += 1
                if isbn_constellation:
                    # look if isbn present in a bnf book
                    if self.is_isbn_in_alignments_bnf(isbn_constellation):
                        non_alignment_isbn_present +=1
                    else:
                        non_alignment_isbn_absent +=1
                else:
                    # missing isbn
                    missing_isbn_constellation +=1
            else: #no url at all
                lines_without_url += 1
                print("empty line", book)

        print("total alignment P", total_alignment)
        print("total non-alignment N", total_non_alignment)
        print("lines without url", lines_without_url)
        print("alignment & isbn matches TP", isbn_equality)
        print("alignment & NOT isbn matches FP", isbn_inequality)
        print("NON alignment & NON isbn present TN", non_alignment_isbn_absent)
        print("NON alignment & isbn present FN", non_alignment_isbn_present)
        print("missing isbn bnf", missing_isbn_bnf)
        print("missing isbn constellation", missing_isbn_constellation)
        print("proportion of correct isbn matches over total number of alignment",
              isbn_equality / (self.alignments_number + utils.EPSILON))
        print("proportion of incorrect isbn matches over total number of alignment",
              isbn_inequality / (self.alignments_number + utils.EPSILON))

    def print_stats(self):
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        print("------------------------------------")
        print("key type", self.key_type)
        print("number of alignments", self.alignments_number)
        print("total number of books", self.total_book_number)
        print("total number of books bnf", self.bnf_book_number)
        print("total number of books constellation", self.constellation_book_number)
        print("total number of collisions", self.collision_number)
        self.compute_alignment_confusion_matrix()

        aligned_books = {}
        average_similarity = 0
        for key in self.all_book_alignments:
            url_constellation = self.all_book_alignments[key].url_constellation
            url_bnf = self.all_book_alignments[key].url_bnf

            if url_bnf and url_constellation:  # proof of alignment because never missing
                aligned_books[key] = self.all_book_alignments[key]
                similarity = utils.jaccard(aligned_books[key].age_range_bnf, aligned_books[key].age_range_constellation)
                # print(
                #     f"key: {key} | lists: {aligned_books[key]} |  similarity between 2 lists: {similarity}")
                average_similarity += similarity
        print(f"average similarity between ages of same {self.key_type}", average_similarity / len(aligned_books))

    def output_csv(self):
        with open(f"alignment_{self.key_type}.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow(["key",
                             "isbn_constellation",
                             "isbn_bnf",
                             "age_range_constellation",
                             "age_range_bnf",
                             "url_constellation",
                             "url_bnf"])
            for key in self.all_book_alignments.keys():
                book_alignment_output = self.all_book_alignments[key]
                writer.writerow([key,
                                 book_alignment_output.isbn_constellation,
                                 book_alignment_output.isbn_bnf,
                                 book_alignment_output.age_range_constellation,
                                 book_alignment_output.age_range_bnf,
                                 book_alignment_output.url_constellation,
                                 book_alignment_output.url_bnf])


stats_name_author = InterDBStats("name_author")
stats_name_author_publisher = InterDBStats("name_author_publisher")
stats_isbn = InterDBStats("isbn")
stats_name_author_publisher_date = InterDBStats("name_author_publisher_date")

# constellations
# ----------------------------------------------------


# load the graph of constellation
g = Graph()
g.parse("../output_constellations.ttl", format="turtle")

# constellation loop
for book in g.subjects(RDF.type, ns1.Book):
    book_name, book_author, age_range_int, url, publication_date, publisher, isbn = \
        utils.extract_data_constellation(g, book)

    book_alignment_constellation = BookAlignment(url_constellation=url,
                                                 isbn_constellation=isbn,
                                                 age_range_constellation=age_range_int)

    name_author_key = utils.create_key(book_name, book_author)
    isbn_key = isbn
    name_author_publisher_key = utils.create_key(book_name, book_author, publisher)
    name_author_publisher_date_key = utils.create_key(book_name, book_author, publisher, publication_date)

    stats_name_author.all_book_alignments[name_author_key] = copy.deepcopy(book_alignment_constellation)
    stats_isbn.all_book_alignments[isbn_key] = copy.deepcopy(book_alignment_constellation)
    stats_name_author_publisher.all_book_alignments[name_author_publisher_key] = \
        copy.deepcopy(book_alignment_constellation)
    stats_name_author_publisher_date.all_book_alignments[name_author_publisher_date_key] = \
        copy.deepcopy(book_alignment_constellation)

    stats_name_author.increment_constellation_book_number()
    stats_isbn.increment_constellation_book_number()
    stats_name_author_publisher.increment_constellation_book_number()
    stats_name_author_publisher_date.increment_constellation_book_number()

# BNF
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_bnf_no_duplicates.ttl", format="turtle")

# BNF loop
for book in g.subjects(RDF.type, ns1.Book):  # O(M)
    book_name, book_author, age_range_int, url, publication_date, publisher, isbn = utils.extract_data_bnf(g, book)
    book_alignment_bnf = BookAlignment(url_bnf=url,
                                       isbn_bnf=isbn,
                                       age_range_bnf=age_range_int)

    name_author_key = utils.create_key(book_name, book_author)
    isbn_key = isbn
    name_author_publisher_key = utils.create_key(book_name, book_author, publisher)
    name_author_publisher_date_key = utils.create_key(book_name, book_author, publisher, publication_date)

    stats_name_author.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_key)
    stats_isbn.align_by_key(copy.deepcopy(book_alignment_bnf), isbn_key)
    stats_name_author_publisher.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_publisher_key)
    stats_name_author_publisher_date.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_publisher_date_key)

    stats_name_author.increment_bnf_book_number()
    stats_isbn.increment_bnf_book_number()
    stats_name_author_publisher.increment_bnf_book_number()
    stats_name_author_publisher_date.increment_bnf_book_number()

stats_name_author.output_csv()
stats_isbn.output_csv()
stats_name_author_publisher.output_csv()
stats_name_author_publisher_date.output_csv()

stats_isbn.print_stats()
stats_name_author.print_stats()
stats_name_author_publisher.print_stats()
stats_name_author_publisher_date.print_stats()

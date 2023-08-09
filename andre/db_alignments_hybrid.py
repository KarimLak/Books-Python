from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
import csv
import utils
import copy
from difflib import SequenceMatcher
from joblib import Parallel, delayed
import logging
import time

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

n_jobs = 12
similarity_ratio = 0.95

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

key_name = "name_author_date_publisher"

time_logger = setup_logger('execution_time_logger',
                           f'{key_name}_approx_{similarity_ratio}_hybrid_execution_time_logfile.log')
stats_logger = setup_logger('stats_logger', f'{key_name}_approx_{similarity_ratio}_hybrid_stats_logfile.log')

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")



def is_key_close_enough_to_another_key(book_key, keys_to_check):
    max_ratio  = 0
    best_key = ""
    for book in keys_to_check:
        s = SequenceMatcher(None, book_key, book)
        ratio = s.ratio()
        if ratio >= similarity_ratio and ratio > max_ratio:
            best_key = book
            max_ratio = ratio
    return best_key, max_ratio

class BookAlignment:
    def __init__(self, isbn_constellation=None, isbn_bnf=None, age_range_constellation=None,
                 age_range_bnf=None, url_constellation=None, url_bnf=None):
        self.isbn_constellation = isbn_constellation
        self.isbn_bnf = isbn_bnf
        self.age_range_constellation = age_range_constellation  # list not used to conserve source in db
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf
        self.url_constellation = url_constellation
        self.similarity_ratio = 0

    def align(self, isbn_bnf, age_range_bnf, url_bnf, similarity_ratio, key_used_to_align):
        self.isbn_bnf = isbn_bnf
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf
        self.similarity_ratio = similarity_ratio
        self.key_used_to_align = key_used_to_align


class InterDBStats:
    def __init__(self, key_type) -> None:
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.bnf_book_number: int = 0
        self.alignments_number: int = 0
        self.collision_number_isbn: int = 0
        self.collision_number_exact_key: int = 0
        self.collision_number_approximate_key: int = 0
        self.key_type = key_type
        self.all_book_alignments= {}

    def increment_alignment_number(self):
        self.alignments_number += 1

    def increment_collision_number_isbn(self):
        self.collision_number_isbn += 1

    def increment_collision_number_exact_key(self):
        self.collision_number_exact_key_key += 1

    def increment_collision_number_approximate_key(self):
        self.collision_number_approximate_key += 1

    def increment_bnf_book_number(self):
        self.bnf_book_number += 1

    def increment_constellation_book_number(self):
        self.constellation_book_number += 1

    def align_hybrid(self,book_alignment, book_key):
        aligned_with_isbn = self.align_by_key_isbn(book_alignment, book_alignment.isbn_bnf)
        if not aligned_with_isbn:
            aligned_with_book_key = self.align_by_key(book_alignment, book_key)
            if not aligned_with_book_key:
                self.align_by_approximate_key(book_alignment, book_key)


    def align_by_approximate_key(self, book_alignment, book_key):
        keys_to_check = list(self.all_book_alignments.keys())
        start_key_finding = time.time()
        batch_size = int(len(keys_to_check)/ n_jobs) + 1
        similar_keys_list = parallel(delayed(is_key_close_enough_to_another_key)(book_key, keys_to_check[i:i + batch_size]) for i in range(0, len(keys_to_check), batch_size))
        end_key_finding = time.time()
        if self.bnf_book_number % 10 == 0:
            time_logger.info(f"time elapsed key finding {end_key_finding - start_key_finding}")
        max_ratio = 0
        best_key = ""
        for key, ratio in similar_keys_list:
            if key:
                if ratio > max_ratio:
                    best_key = key
                    max_ratio = ratio
        if best_key:
            if not self.all_book_alignments[best_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[best_key].align(isbn_bnf=book_alignment.isbn_bnf,
                                                         age_range_bnf=book_alignment.age_range_bnf,
                                                         url_bnf=book_alignment.url_bnf,
                                                         similarity_ratio = max_ratio,
                                                         key_used_to_align = book_key)
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align approximate")

            else:
                self.increment_collision_number_approximate_key()  # increase if bnf data already present: doublon inside bnf


        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    def isbn_alignment(self, isbn_to_match):
        for candidate_key in self.all_book_alignments.keys():
            candidate_isbn = self.all_book_alignments[candidate_key].isbn_constellation
            if candidate_isbn == isbn_to_match:
                return candidate_key
        return ""

    def align_by_key_isbn(self, book_alignment, book_key_to_match):  # True if alignment in this call or already done (collision)
        matched_key = self.isbn_alignment(book_alignment.isbn_bnf)
        if matched_key:
            if not self.all_book_alignments[matched_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[matched_key].align(isbn_bnf=book_alignment.isbn_bnf,
                                                         age_range_bnf=book_alignment.age_range_bnf,
                                                         url_bnf=book_alignment.url_bnf,
                                                            similarity_ratio = -1,
                                                            key_used_to_align="isbn")
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align isbn")
                return True
            else:
                self.increment_collision_number_isbn()  # increase if bnf data already present: doublon inside bnf
                return True # si collision -> deja aligné
        else:
            self.all_book_alignments[book_key_to_match] = book_alignment  # bnf data gets into the dict without alignment
            return False

    def align_by_key(self, book_alignment, book_key_to_match):  # True if alignment in this call or already done (collision)
        if book_key_to_match in self.all_book_alignments:
            if not self.all_book_alignments[book_key_to_match].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key_to_match].align(isbn_bnf=book_alignment.isbn_bnf,
                                                                  age_range_bnf=book_alignment.age_range_bnf,
                                                                  url_bnf=book_alignment.url_bnf,
                                                                  similarity_ratio = -1,
                                                                  key_used_to_align="exact")
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align exact")
                return True
            else:
                self.increment_collision_number_exact_key()
                return True # si collision -> deja aligné
        else:
            self.all_book_alignments[book_key_to_match] = book_alignment  # bnf data gets into the dict without alignment
            return False

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
            stats_logger.error(f"wrong source in is_isbn_in_alignments, {source} doesn't exist")
        return False

    def compute_alignment_confusion_matrix(self):

        stats_logger.info("-----")
        isbn_equality = 0 # TP
        isbn_inequality = 0 # FP
        missing_isbn_bnf_in_negatives = 0
        missing_isbn_constellation_in_negatives = 0
        missing_isbn_constellation_in_positives = 0
        missing_isbn_bnf_in_positives = 0
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
                    missing_isbn_constellation_in_positives += 1
                if not isbn_bnf:
                    missing_isbn_bnf_in_positives += 1
            elif url_bnf and not url_constellation: # non-alignment: only 1 bnf present
                total_non_alignment += 1
                if isbn_bnf:
                    # look if isbn present in a constellation book
                    if self.is_isbn_in_alignments_constellation(isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent +=1
                else:
                    missing_isbn_bnf_in_negatives += 1
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
                    missing_isbn_constellation_in_negatives +=1
            else: #no url at all
                lines_without_url += 1
                stats_logger("empty line", book)

        stats_logger.info(f"total alignment P {total_alignment}")
        stats_logger.info(f"total non-alignment N {total_non_alignment}")
        stats_logger.info(f"lines without url {lines_without_url}")
        stats_logger.info(f"alignment & isbn matches TP {isbn_equality}")
        stats_logger.info(f"alignment & NOT isbn matches FP {isbn_inequality}")
        stats_logger.info(f"NON alignment & NON isbn present TN {non_alignment_isbn_absent}")
        stats_logger.info(f"NON alignment & isbn present FN {non_alignment_isbn_present}")
        stats_logger.info(f"missing isbn bnf for positives {missing_isbn_bnf_in_positives}")
        stats_logger.info(f"missing isbn constellation for positives {missing_isbn_constellation_in_positives}")
        stats_logger.info(f"missing isbn bnf for negatives {missing_isbn_bnf_in_negatives}")
        stats_logger.info(f"missing isbn constellation for negatives {missing_isbn_constellation_in_negatives}")
        stats_logger.info(f"proportion of correct isbn matches over total number of alignment "
                          f"{isbn_equality / (self.alignments_number + utils.EPSILON)}")
        stats_logger.info(f"proportion of incorrect isbn matches over total number of alignment "
                          f"{isbn_inequality / (self.alignments_number + utils.EPSILON)}")

    def print_stats(self):
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        stats_logger.info("------------------------------------")
        stats_logger.info(f"key type {self.key_type}")
        stats_logger.info(f"number of alignments {self.alignments_number}")
        stats_logger.info(f"total number of books {self.total_book_number}")
        stats_logger.info(f"total number of books bnf {self.bnf_book_number}")
        stats_logger.info(f"total number of books constellation {self.constellation_book_number}")
        stats_logger.info(f"total number of collisions isbn {self.collision_number_isbn}")
        stats_logger.info(f"total number of collisions exact key {self.collision_number_exact_key}")
        stats_logger.info(f"total number of collisions approximate key {self.collision_number_approximate_key}")
        self.compute_alignment_confusion_matrix()

        aligned_books = {}
        average_similarity = 0
        # for key in self.all_book_alignments:
        #     url_constellation = self.all_book_alignments[key].url_constellation
        #     url_bnf = self.all_book_alignments[key].url_bnf
        #
        #     if url_bnf and url_constellation:  # proof of alignment because never missing
        #         aligned_books[key] = self.all_book_alignments[key]
        #         similarity = utils.jaccard(aligned_books[key].age_range_bnf, aligned_books[key].age_range_constellation)
        #         # print(
        #         #     f"key: {key} | lists: {aligned_books[key]} |  similarity between 2 lists: {similarity}")
        #         average_similarity += similarity
        # print(f"average similarity between ages of same {self.key_type}", average_similarity / len(aligned_books))

    def output_csv(self):
        with open(f"hybrid_alignment_{self.key_type}_ratio_{similarity_ratio}.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow(["key",
                             "similarity ratio",
                             "key used to align",
                             "isbn_constellation",
                             "isbn_bnf",
                             "url_constellation",
                             "url_bnf"])
            for key in self.all_book_alignments.keys():
                book_alignment_output: BookAlignment = self.all_book_alignments[key]
                writer.writerow([key,
                                 book_alignment_output.similarity_ratio,
                                 book_alignment_output.key_used_to_align,
                                 book_alignment_output.isbn_constellation,
                                 book_alignment_output.isbn_bnf,
                                 book_alignment_output.url_constellation,
                                 book_alignment_output.url_bnf])


# stats_name_author = InterDBStats("name_author")
# stats_name_author_publisher = InterDBStats("name_author_publisher")
# stats_isbn = InterDBStats("isbn")
# stats_name_author_publisher_date = InterDBStats("name_author_publisher_date")
stats = InterDBStats(key_name)

# constellations
# ----------------------------------------------------


# load the graph of constellation
g = Graph()
g.parse("../output_constellations.ttl", format="turtle")
# g.parse("data/data as of 04 august/output_constellations_updated.ttl", format="turtle")
# g.parse("output_constellations_light_extended.ttl", format="turtle")

# constellation loop

for book in g.subjects(RDF.type, ns1.Book):
    book_data: utils.RdfBookData = \
        utils.remove_special_chars(
            utils.remove_accents(
                utils.lower(
                    utils.remove_spaces(
                        utils.extract_data_constellation(g, book)))))

    book_alignment_constellation = BookAlignment(url_constellation=book_data.url,
                                                 isbn_constellation=book_data.isbn,
                                                 age_range_constellation=book_data.age_range_int)

    # name_author_key = utils.create_key(book_name, book_author)
    isbn_key = book_data.isbn
    # name_author_publisher_key = utils.create_key(book_name, book_author, publisher)
    name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                            book_author=book_data.book_author,
                                            publisher=book_data.publisher,
                                            publication_date=book_data.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data.book_name,
    #                                         book_author=book_data.book_author,
    #                                         publication_date=book_data.publication_date)


    stats.all_book_alignments[name_author_publisher_date_key] = \
        copy.deepcopy(book_alignment_constellation)


    stats.increment_constellation_book_number()

print("constellation book number", stats.constellation_book_number)
# BNF
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_bnf.ttl", format="turtle")
# g.parse("data/data as of 04 august/27jul_local_output_bnf_no_duplicates.ttl", format="turtle")
# g.parse("output_bnf_light_extended.ttl", format="turtle")

# BNF loop

with Parallel(n_jobs=n_jobs) as parallel:
    for book in g.subjects(RDF.type, ns1.Book):  # O(M)
        book_data: utils.RdfBookData = \
            utils.remove_special_chars(
                utils.remove_accents(
                    utils.lower(
                        utils.remove_spaces(
                            utils.extract_data_bnf(g, book)))))
        book_alignment_bnf = BookAlignment(url_bnf=book_data.url,
                                           isbn_bnf=book_data.isbn,
                                           age_range_bnf=book_data.age_range_int)

        name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                          book_author=book_data.book_author,
                                                          publisher=book_data.publisher,
                                                          publication_date=book_data.publication_date)
        # name_author_date_key = utils.create_key(book_name=book_data.book_name,
        #                                         book_author=book_data.book_author,
        #                                         publication_date=book_data.publication_date)


        start = time.time()
        stats.align_hybrid(copy.deepcopy(book_alignment_bnf), name_author_publisher_date_key)
        end = time.time()
        if stats.bnf_book_number % 10 == 0:
            time_logger.info(f"book no {stats.bnf_book_number}")
            time_logger.info(f"time elapsed 1 book {end - start}")
            time_logger.info("##################")
            time_logger.info("")

        # stats_name_author.increment_bnf_book_number()
        # stats_isbn.increment_bnf_book_number()
        # stats_name_author_publisher.increment_bnf_book_number()
        stats.increment_bnf_book_number()


# stats_name_author.output_csv()
# stats_isbn.output_csv()
# stats_name_author_publisher.output_csv()
stats.output_csv()

# stats_isbn.print_stats()
# stats_name_author.print_stats()
# stats_name_author_publisher.print_stats()
stats.print_stats()
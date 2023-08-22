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

N_JOBS = 12
SIMILARITY_RATIO = 0.9


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


key_name = "name_author_publisher_date"

time_logger = setup_logger('execution_time_logger',
                           f'{key_name}_approx_{SIMILARITY_RATIO}_hybrid_execution_time_logfile.log')
stats_logger = setup_logger('stats_logger', f'{key_name}_approx_{SIMILARITY_RATIO}_hybrid_stats_logfile.log')

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


def is_key_close_enough_to_another_key(book_key, keys_to_check):
    max_ratio = 0
    best_key = ""
    for key_to_check in keys_to_check:
        s = SequenceMatcher(None, book_key, key_to_check)
        ratio = s.ratio()
        if ratio >= SIMILARITY_RATIO and ratio > max_ratio:
            best_key = key_to_check
            max_ratio = ratio
    return best_key, max_ratio


class BookAlignment:
    def __init__(self, isbn_constellation=None, isbn_bnf=None, age_range_constellation=None,
                 age_range_bnf=None, url_constellation=None, url_bnf=None, url_lurelu=None, isbn_lurelu=None):
        self.similarity_ratio_lurelu = 0
        self.key_used_to_align_bnf = None
        self.key_used_to_align_lurelu = None

        self.isbn_constellation = isbn_constellation
        self.age_range_constellation = age_range_constellation  # list not used to conserve source in db
        self.url_constellation = url_constellation

        self.isbn_bnf = isbn_bnf
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf

        self.url_lurelu = url_lurelu
        self.isbn_lurelu = isbn_lurelu


    def align_bnf(self, key_used_to_align_bnf=None, isbn_bnf=None,url_bnf=None):
        self.key_used_to_align_bnf = key_used_to_align_bnf
        self.isbn_bnf = isbn_bnf
        self.url_bnf = url_bnf
    def align_lurelu(self,  isbn_lurelu=None,  url_lurelu=None, similarity_ratio_lurelu=None, key_used_to_align_lurelu=None):
        self.similarity_ratio_lurelu = similarity_ratio_lurelu
        self.key_used_to_align_lurelu = key_used_to_align_lurelu
        self.url_lurelu = url_lurelu
        self.isbn_lurelu = isbn_lurelu


class InterDBStats:
    def __init__(self, key_type) -> None:
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.bnf_book_number: int = 0
        self.alignments_number_bnf: int = 0
        self.alignments_number_lurelu: int = 0
        self.collision_number_isbn: int = 0
        self.collision_number_exact_key_bnf: int = 0
        self.collision_number_exact_key_lurelu: int = 0
        self.collision_number_approximate_key_bnf: int = 0
        self.collision_number_approximate_key_lurelu: int = 0
        self.lurelu_book_number = 0
        self.key_type = key_type
        self.all_book_alignments = {}

    def increment_alignment_number_bnf(self):
        self.alignments_number_bnf += 1

    def increment_alignment_number_lurelu(self):
        self.alignments_number_lurelu += 1

    def increment_collision_number_isbn(self):
        self.collision_number_isbn += 1

    def increment_collision_number_exact_key_bnf(self):
        self.collision_number_exact_key_bnf += 1

    def increment_collision_number_exact_key_lurelu(self):
        self.collision_number_exact_key_lurelu += 1

    def increment_collision_number_approximate_key_bnf(self):
        self.collision_number_approximate_key_bnf += 1

    def increment_collision_number_approximate_key_lurelu(self):
        self.collision_number_approximate_key_lurelu += 1

    def increment_bnf_book_number(self):
        self.bnf_book_number += 1

    def increment_constellation_book_number(self):
        self.constellation_book_number += 1

    def increment_lurelu_book_number(self):
        self.lurelu_book_number += 1

    def align_hybrid(self, book_alignment, book_key):
        aligned_with_isbn = self.align_by_key_isbn(book_alignment, book_key)  # pass the key in case of non alignment
        if not aligned_with_isbn:
            aligned_with_book_key = self.align_by_exact_key_bnf(book_alignment, book_key)
            # if not aligned_with_book_key:
            #     self.align_by_approximate_key(book_alignment, book_key)

    def align_hybrid_without_isbn(self, book_alignment, book_key):
        aligned_with_book_key = self.align_by_exact_key_lurelu(book_alignment, book_key)  # lurelu is aligned without isbn
        if not aligned_with_book_key:
            self.align_by_approximate_key_lurelu(book_alignment, book_key)

    def align_by_approximate_key_lurelu(self, book_alignment, book_key):
        keys_to_check = list(self.all_book_alignments.keys())
        start_key_finding = time.time()
        batch_size = int(len(keys_to_check) / N_JOBS) + 1
        similar_keys_list = parallel(
            delayed(is_key_close_enough_to_another_key)(book_key, keys_to_check[i:i + batch_size]) for i in
            range(0, len(keys_to_check), batch_size))
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
            if not self.all_book_alignments[best_key].url_lurelu:  # not a collision: lurelu data not present
                self.all_book_alignments[best_key].align_lurelu(isbn_lurelu=book_alignment.isbn_lurelu,
                                                         url_lurelu=book_alignment.url_lurelu,
                                                         similarity_ratio_lurelu=max_ratio,
                                                         key_used_to_align_lurelu=book_key)
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align approximate")

            else:
                self.increment_collision_number_approximate_key_lurelu()  # increase if bnf data already present: doublon inside bnf
        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    def isbn_alignment(self, isbn_to_match):
        for candidate_key in self.all_book_alignments.keys():
            candidate_isbn = self.all_book_alignments[candidate_key].isbn_constellation
            if candidate_isbn == isbn_to_match:
                return candidate_key
        return ""

    # Returns True if alignment in this call or already done (collision)
    # We only align constellation & bnf with isbn for now
    def align_by_key_isbn(self, book_alignment, book_key):
        matched_key = self.isbn_alignment(book_alignment.isbn_bnf)
        if matched_key:
            if not self.all_book_alignments[matched_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[matched_key].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                            url_bnf=book_alignment.url_bnf,
                                                            key_used_to_align_bnf="isbn")
                self.increment_alignment_number_bnf()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align isbn")
                return True
            else:
                self.increment_collision_number_isbn()  # increase if bnf data already present: doublon inside bnf
                return True  # if collision -> already aligned
        else:
            self.all_book_alignments[
                book_key] = book_alignment  # bnf data gets into the dict with its own key without alignment
            return False

    # Returns True if alignment in this call or already done (collision)
    def align_by_exact_key_bnf(self, book_alignment, book_key_to_match):
        if book_key_to_match in self.all_book_alignments:
            if not self.all_book_alignments[book_key_to_match].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key_to_match].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                                  url_bnf=book_alignment.url_bnf,
                                                                  key_used_to_align_bnf="exact")
                self.increment_alignment_number_bnf()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align exact")
                return True
            else:
                self.increment_collision_number_exact_key_bnf()
                return True  # si collision -> deja aligné
        else:
            self.all_book_alignments[
                book_key_to_match] = book_alignment  # bnf data gets into the dict without alignment
            return False

    def align_by_exact_key_lurelu(self, book_alignment, book_key_to_match):
        if book_key_to_match in self.all_book_alignments:
            if not self.all_book_alignments[book_key_to_match].url_lurelu:  # not a collision: bnf data not present
                self.all_book_alignments[book_key_to_match].align_lurelu(isbn_lurelu=book_alignment.isbn_lurelu,
                                                                  url_lurelu=book_alignment.url_lurelu,
                                                                  similarity_ratio_lurelu=-1,
                                                                  key_used_to_align_lurelu="exact")
                self.increment_alignment_number_lurelu()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align exact")
                return True
            else:
                self.increment_collision_number_exact_key_lurelu()
                return True  # if collision -> already aligned
        else:
            self.all_book_alignments[
                book_key_to_match] = book_alignment  # bnf data gets into the dict without alignment
            return False

    def is_isbn_in_alignments_bnf(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "bnf")

    def is_isbn_in_alignments_constellation(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "constellation")

    def is_isbn_in_alignments_constellation_bnf(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "constellation_or_bnf")

    def is_isbn_in_alignments_lurelu(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "lurelu")

    def is_isbn_in_alignments(self, target_isbn, source) -> bool:
        if source == "bnf":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_bnf:
                    return True
        elif source == "constellation":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_constellation:
                    return True
        elif source == "lurelu":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_lurelu:
                    return True
        elif source == "constellation_or_bnf":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_constellation or target_isbn == \
                        self.all_book_alignments[book_alignment].isbn_bnf:
                    return True
        else:
            stats_logger.error(f"wrong source in is_isbn_in_alignments, {source} doesn't exist")
        return False

    def compute_alignment_confusion_matrix_validation(self):

        stats_logger.info("----- validation set")
        isbn_equality = 0  # TP
        isbn_inequality = 0  # FP
        missing_isbn_bnf_in_negatives = 0
        missing_isbn_constellation_in_negatives = 0
        missing_isbn_constellation_in_positives = 0
        missing_isbn_bnf_in_positives = 0
        total_non_alignment = 0  # N
        total_alignment = 0  # P
        non_alignment_isbn_present = 0  # FN
        non_alignment_isbn_absent = 0  # TN
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
            elif url_bnf and not url_constellation:  # non-alignment: only 1 bnf present
                total_non_alignment += 1
                if isbn_bnf:
                    # look if isbn present in a constellation book
                    if self.is_isbn_in_alignments_constellation(isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    missing_isbn_bnf_in_negatives += 1
            elif not url_bnf and url_constellation:
                total_non_alignment += 1
                if isbn_constellation:
                    # look if isbn present in a bnf book
                    if self.is_isbn_in_alignments_bnf(isbn_constellation):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    # missing isbn
                    missing_isbn_constellation_in_negatives += 1
            elif self.all_book_alignments[book_key].url_lurelu:
                continue # if lurelu url, do nothing
            else:  # no url at all
                lines_without_url += 1
                stats_logger.info("empty line", book)

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

    def compute_alignment_confusion_matrix_test(self):

        stats_logger.info("----- test set")
        isbn_equality = 0  # TP
        isbn_inequality = 0  # FP
        missing_isbn_bnf_constellation_in_negatives = 0
        missing_isbn_lurelu_in_negatives = 0
        missing_isbn_bnf_constellation_in_positives = 0
        missing_isbn_lurelu_in_positives = 0
        total_non_alignment = 0  # N
        total_alignment = 0  # P
        non_alignment_isbn_present = 0  # FN
        non_alignment_isbn_absent = 0  # TN
        lines_without_url = 0
        for book_key in self.all_book_alignments:
            book_alignment: BookAlignment = self.all_book_alignments[book_key]

            isbn_constellation = book_alignment.isbn_constellation
            isbn_bnf = book_alignment.isbn_bnf
            isbn_lurelu = book_alignment.isbn_lurelu

            url_constellation = book_alignment.url_constellation
            url_bnf = book_alignment.url_bnf
            url_lurelu = book_alignment.url_lurelu

            if url_lurelu and (url_bnf or url_constellation):  # proof of alignment because never missing
                total_alignment += 1
                if isbn_lurelu and (isbn_constellation or isbn_bnf):
                    if isbn_lurelu == isbn_constellation or isbn_lurelu == isbn_bnf:
                        isbn_equality += 1
                    else:
                        isbn_inequality += 1
                if not isbn_lurelu:
                    missing_isbn_lurelu_in_positives += 1
                if not isbn_bnf and not isbn_constellation:
                    missing_isbn_bnf_constellation_in_positives += 1
            elif not url_lurelu and (url_bnf or url_constellation):  # non-alignment: only bnf or constellation present
                total_non_alignment += 1
                if isbn_bnf and not isbn_constellation:  # look if isbn present in a lurelu book
                    if self.is_isbn_in_alignments_lurelu(isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                elif isbn_constellation and not isbn_bnf:
                    if self.is_isbn_in_alignments_lurelu(isbn_constellation):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                elif isbn_constellation and isbn_bnf:
                    if self.is_isbn_in_alignments_lurelu(isbn_constellation) or self.is_isbn_in_alignments_lurelu(
                            isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    missing_isbn_bnf_constellation_in_negatives += 1
            elif url_lurelu and not (url_bnf or url_constellation):
                total_non_alignment += 1
                if isbn_lurelu:
                    # look if isbn present in a bnf book
                    if self.is_isbn_in_alignments_bnf(isbn_lurelu) or self.is_isbn_in_alignments_constellation(
                            isbn_lurelu):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    # missing isbn
                    missing_isbn_lurelu_in_negatives += 1
            else:  # no url at all
                lines_without_url += 1
                stats_logger.info("empty line", book)

        stats_logger.info(f"total alignment P {total_alignment}")
        stats_logger.info(f"total non-alignment N {total_non_alignment}")
        stats_logger.info(f"lines without url {lines_without_url}")
        stats_logger.info(f"alignment & isbn matches TP {isbn_equality}")
        stats_logger.info(f"alignment & NOT isbn matches FP {isbn_inequality}")
        stats_logger.info(f"NON alignment & NON isbn present TN {non_alignment_isbn_absent}")
        stats_logger.info(f"NON alignment & isbn present FN {non_alignment_isbn_present}")
        stats_logger.info(f"missing isbn bnf or constellation for positives {missing_isbn_bnf_constellation_in_positives}")
        stats_logger.info(f"missing isbn lurelu for positives {missing_isbn_lurelu_in_positives}")
        stats_logger.info(f"missing isbn bnf or constellation for negatives {missing_isbn_bnf_constellation_in_negatives}")
        stats_logger.info(f"missing isbn lurelu for negatives {missing_isbn_lurelu_in_negatives}")

    def print_stats(self):
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        stats_logger.info("------------------------------------")
        stats_logger.info(f"key type {self.key_type}")
        stats_logger.info(f"number of alignments bnf {self.alignments_number_bnf}")
        stats_logger.info(f"number of alignments lurelu {self.alignments_number_lurelu}")
        stats_logger.info(f"total number of books {self.total_book_number}")
        stats_logger.info(f"total number of books bnf {self.bnf_book_number}")
        stats_logger.info(f"total number of books constellation {self.constellation_book_number}")
        stats_logger.info(f"total number of books lurelu {self.lurelu_book_number}")
        stats_logger.info(f"total number of collisions isbn {self.collision_number_isbn}")
        stats_logger.info(f"total number of collisions exact key bnf {self.collision_number_exact_key_bnf}")
        stats_logger.info(f"total number of collisions exact key lurelu {self.collision_number_exact_key_lurelu}")
        stats_logger.info(f"total number of collisions approximate key lurelu {self.collision_number_approximate_key_lurelu}")
        self.compute_alignment_confusion_matrix_validation()
        self.compute_alignment_confusion_matrix_test()

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
        with open(f"hybrid_alignment_{self.key_type}_ratio_{SIMILARITY_RATIO}.csv", "w", encoding='utf-8',
                  newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow(["key",
                             "key used to align bnf",
                             "isbn_constellation",
                             "isbn_bnf",
                             "isbn_lurelu",
                             "key used to align lurelu",
                             "similarity ratio",
                             "url_constellation",
                             "url_bnf",
                             "url_lurelu"])
            for key in self.all_book_alignments.keys():
                book_alignment_output: BookAlignment = self.all_book_alignments[key]
                writer.writerow([key,
                                 book_alignment_output.key_used_to_align_bnf,
                                 book_alignment_output.isbn_constellation,
                                 book_alignment_output.isbn_bnf,
                                 book_alignment_output.isbn_lurelu,
                                 book_alignment_output.key_used_to_align_lurelu,
                                 book_alignment_output.similarity_ratio_lurelu,
                                 book_alignment_output.url_constellation,
                                 book_alignment_output.url_bnf,
                                 book_alignment_output.url_lurelu])


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
    # isbn_key = book_data.isbn
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



# LURELU
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_lurelu_updated.ttl", format="turtle")
with Parallel(n_jobs=N_JOBS) as parallel:
    for book in g.subjects(RDF.type, ns1.Book):  # O(M)
        book_data: utils.RdfBookData = \
            utils.remove_special_chars(
                utils.remove_accents(
                    utils.lower(
                        utils.remove_spaces(
                            utils.extract_data_lurelu(g, book)))))
        book_alignment_lurelu = BookAlignment(url_lurelu=book_data.url,
                                              isbn_lurelu=book_data.isbn)

        name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                          book_author=book_data.book_author,
                                                          publisher=book_data.publisher,
                                                          publication_date=book_data.publication_date)
        # name_author_date_key = utils.create_key(book_name=book_data.book_name,
        #                                         book_author=book_data.book_author,
        #                                         publication_date=book_data.publication_date)

        start = time.time()
        # stats.align_by_approximate_key_lurelu(book_alignment_lurelu, name_author_publisher_date_key)
        stats.align_hybrid_without_isbn(copy.deepcopy(book_alignment_lurelu), name_author_publisher_date_key)
        end = time.time()

        if stats.lurelu_book_number % 10 == 0:
            time_logger.info(f"book no {stats.lurelu_book_number}")
            time_logger.info(f"time elapsed 1 book {end - start}")
            time_logger.info("##################")
            time_logger.info("")

        # stats_name_author.increment_bnf_book_number()
        # stats_isbn.increment_bnf_book_number()
        # stats_name_author_publisher.increment_bnf_book_number()
        stats.increment_lurelu_book_number()

# stats_name_author.output_csv()
# stats_isbn.output_csv()
# stats_name_author_publisher.output_csv()
stats.output_csv()

# stats_isbn.print_stats()
# stats_name_author.print_stats()
# stats_name_author_publisher.print_stats()
stats.print_stats()

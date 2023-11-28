import time
from logging import Logger

from joblib import delayed
from book_alignment import BookAlignment
import utils
import csv
from interdbstats import InterDbStats


class InterDbStatsHybrid(InterDbStats):
    def __init__(self, key_type, stats_logger, time_logger, SIMILARITY_RATIO, N_JOBS) -> None:
        super().__init__(key_type, stats_logger)
        self.time_logger: Logger = time_logger
        self.SIMILARITY_RATIO: int = SIMILARITY_RATIO
        self.N_JOBS: int = N_JOBS
        self.alignments_number_bnf: int = 0
        self.alignments_number_lurelu: int = 0
        self.collision_number_isbn: int = 0
        self.collision_number_exact_key_bnf: int = 0
        self.collision_number_exact_key_lurelu: int = 0
        self.collision_number_approximate_key_bnf: int = 0
        self.collision_number_approximate_key_lurelu: int = 0
        self.lurelu_book_number = 0
        self.alignment_method = "hybrid"

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
        aligned_with_isbn = self.align_by_key_isbn(book_alignment, book_alignment.isbn_bnf)
        if not aligned_with_isbn:
            aligned_with_ean = self.align_by_key_isbn(book_alignment, book_alignment.ean_bnf)
            if not aligned_with_ean:
                aligned_with_book_key = self.align_by_exact_key_bnf(book_alignment, book_key)
            # if not aligned_with_book_key:
            #     self.align_by_approximate_key(book_alignment, book_key)

    def align_hybrid_without_isbn(self, book_alignment, book_key, parallel):
        aligned_with_book_key = self.align_by_exact_key_lurelu(book_alignment,
                                                               book_key)  # lurelu is aligned without isbn
        # if not aligned_with_book_key:
        #     self.align_by_approximate_key_lurelu(book_alignment, book_key, parallel)

    def align_by_approximate_key_lurelu(self, book_alignment, book_key, parallel):
        keys_to_check = list(self.all_book_alignments.keys())
        start_key_finding = time.time()
        batch_size = int(len(keys_to_check) / self.N_JOBS) + 1
        similar_keys_list = parallel(
            delayed(utils.is_key_close_enough_to_another_key)(book_key, keys_to_check[i:i + batch_size],
                                                              self.SIMILARITY_RATIO) for i in
            range(0, len(keys_to_check), batch_size))
        end_key_finding = time.time()
        if self.bnf_book_number % 10 == 0:
            self.time_logger.info(f"time elapsed key finding {end_key_finding - start_key_finding}")
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
                                                                key_used_to_align_lurelu=book_key,
                                                                uri_lurelu=book_alignment.uri_lurelu)

                self.increment_alignment_number_lurelu()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align approximate")

            else:
                self.increment_collision_number_approximate_key_lurelu()  # increase if lurelu data already present: doublon inside lurelu
        else:
            self.all_book_alignments[
                book_key] = book_alignment  # lurelu data gets into the dict without alignment because could not find suitable candidate and no other methods to test

    def isbn_alignment(self, isbn_to_match):
        for candidate_key in self.all_book_alignments.keys():
            candidate_isbn = self.all_book_alignments[candidate_key].isbn_constellation
            if candidate_isbn == isbn_to_match:
                return candidate_key
        return ""

    # Returns True if alignment in this call or already done (collision)
    # We only align constellation & bnf with isbn for now
    def align_by_key_isbn(self, book_alignment, isbn):
        matched_key = self.isbn_alignment(isbn)
        if matched_key:
            if not self.all_book_alignments[matched_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[matched_key].align_bnf(key_used_to_align_bnf="isbn",
                                                                isbn_bnf=book_alignment.isbn_bnf,
                                                                url_bnf=book_alignment.url_bnf,
                                                                uri_bnf=book_alignment.uri_bnf)
                self.increment_alignment_number_bnf()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align isbn")
                return True
            else:
                self.increment_collision_number_isbn()  # increase if bnf data already present: doublon inside bnf
                return True  # if collision -> already aligned
        else:  # if not aligned with isbn, return without registering key in dict so it can be aligned with exact
            return False

    # Returns True if alignment in this call or already done (collision)
    def align_by_exact_key_bnf(self, book_alignment, book_key_to_match):
        if book_key_to_match in self.all_book_alignments:
            if not self.all_book_alignments[book_key_to_match].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key_to_match].align_bnf(key_used_to_align_bnf="exact",
                                                                      isbn_bnf=book_alignment.isbn_bnf,
                                                                      url_bnf=book_alignment.url_bnf,
                                                                      uri_bnf=book_alignment.uri_bnf)

                self.increment_alignment_number_bnf()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align exact")
                return True
            else:
                self.increment_collision_number_exact_key_bnf()
                return True  # si collision -> deja aligné
        else:
            self.all_book_alignments[
                book_key_to_match] = book_alignment  # bnf data gets into the dict without alignment (remove if trying approximative alignment after)
            return False

    def align_by_exact_key_lurelu(self, book_alignment, book_key_to_match):
        if book_key_to_match in self.all_book_alignments:
            if not self.all_book_alignments[book_key_to_match].url_lurelu:  # not a collision: bnf data not present
                self.all_book_alignments[book_key_to_match].align_lurelu(isbn_lurelu=book_alignment.isbn_lurelu,
                                                                         url_lurelu=book_alignment.url_lurelu,
                                                                         similarity_ratio_lurelu=-1,
                                                                         key_used_to_align_lurelu="exact",
                                                                         uri_lurelu=book_alignment.uri_lurelu)
                self.increment_alignment_number_lurelu()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_
                print("align exact")
                return True
            else:
                self.increment_collision_number_exact_key_lurelu()
                return True  # if collision -> already aligned
        else:  # if not aligned with exact, return without registering key in dict, so it can be aligned with approx
            return False

    def compute_alignment_confusion_matrix_test(self):

        self.stats_logger.info("----- test set")
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
                self.stats_logger.info("empty line", book_key)

        self.stats_logger.info(f"total alignment P {total_alignment}")
        self.stats_logger.info(f"total non-alignment N {total_non_alignment}")
        self.stats_logger.info(f"lines without url {lines_without_url}")
        self.stats_logger.info(f"alignment & isbn matches TP {isbn_equality}")
        self.stats_logger.info(f"alignment & NOT isbn matches FP {isbn_inequality}")
        self.stats_logger.info(f"NON alignment & NON isbn present TN {non_alignment_isbn_absent}")
        self.stats_logger.info(f"NON alignment & isbn present FN {non_alignment_isbn_present}")
        self.stats_logger.info(
            f"missing isbn bnf or constellation for positives {missing_isbn_bnf_constellation_in_positives}")
        self.stats_logger.info(f"missing isbn lurelu for positives {missing_isbn_lurelu_in_positives}")
        self.stats_logger.info(
            f"missing isbn bnf or constellation for negatives {missing_isbn_bnf_constellation_in_negatives}")
        self.stats_logger.info(f"missing isbn lurelu for negatives {missing_isbn_lurelu_in_negatives}")

    def print_stats(self):
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        self.stats_logger.info("------------------------------------")
        self.stats_logger.info(f"key type {self.key_type}")
        self.stats_logger.info(f"number of alignments bnf {self.alignments_number_bnf}")
        self.stats_logger.info(f"number of alignments lurelu {self.alignments_number_lurelu}")
        self.stats_logger.info(f"total number of books {self.total_book_number}")
        self.stats_logger.info(f"total number of books bnf {self.bnf_book_number}")
        self.stats_logger.info(f"total number of books constellation {self.constellation_book_number}")
        self.stats_logger.info(f"total number of books lurelu {self.lurelu_book_number}")
        self.stats_logger.info(f"total number of collisions isbn {self.collision_number_isbn}")
        self.stats_logger.info(f"total number of collisions exact key bnf {self.collision_number_exact_key_bnf}")
        self.stats_logger.info(f"total number of collisions exact key lurelu {self.collision_number_exact_key_lurelu}")
        self.stats_logger.info(
            f"total number of collisions approximate key lurelu {self.collision_number_approximate_key_lurelu}")
        self.compute_alignment_confusion_matrix_validation()
        self.compute_alignment_confusion_matrix_test()

    def output_csv(self):
        with open(f"hybrid_alignment_{self.key_type}_ratio_{self.SIMILARITY_RATIO}.csv", "w", encoding='utf-8',
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

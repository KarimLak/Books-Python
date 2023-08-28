import utils
import csv
from interdbstats import InterDbStats

class InterDbStatsExact(InterDbStats):
    def __init__(self, key_type, stats_logger) -> None:
        super().__init__(key_type, stats_logger)
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.alignment_method = "exact"


    def align_by_key(self, book_alignment, book_key):  # O(1)
        if book_key in self.all_book_alignments:
            if not self.all_book_alignments[book_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                             url_bnf=book_alignment.url_bnf)
                self.increment_alignment_number()  # bnf data already present because of key doublon  inside bnf; independant of alignment (may be present without alignment_

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf


        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    # def compute_alignment_confusion_matrix(self):
    #     self.stats_logger.info("-----")
    #     isbn_equality = 0  # TP
    #     isbn_inequality = 0  # FP
    #     missing_isbn_bnf_in_negatives = 0
    #     missing_isbn_constellation_in_negatives = 0
    #     missing_isbn_constellation_in_positives = 0
    #     missing_isbn_bnf_in_positives = 0
    #     total_non_alignment = 0  # N
    #     total_alignment = 0  # P
    #     non_alignment_isbn_present = 0  # FN
    #     non_alignment_isbn_absent = 0  # TN
    #     lines_without_url = 0
    #     for book_key in self.all_book_alignments:
    #         isbn_constellation = self.all_book_alignments[book_key].isbn_constellation
    #         isbn_bnf = self.all_book_alignments[book_key].isbn_bnf
    #
    #         url_constellation = self.all_book_alignments[book_key].url_constellation
    #         url_bnf = self.all_book_alignments[book_key].url_bnf
    #
    #         if url_bnf and url_constellation:  # proof of alignment because never missing
    #             total_alignment += 1
    #             if isbn_constellation and isbn_bnf:
    #                 if isbn_bnf == isbn_constellation:
    #                     isbn_equality += 1
    #                 else:
    #                     isbn_inequality += 1
    #             if not isbn_constellation:
    #                 missing_isbn_constellation_in_positives += 1
    #             if not isbn_bnf:
    #                 missing_isbn_bnf_in_positives += 1
    #         elif url_bnf and not url_constellation:  # non-alignment: only 1 bnf present
    #             total_non_alignment += 1
    #             if isbn_bnf:
    #                 # look if isbn present in a constellation book
    #                 if self.is_isbn_in_alignments_constellation(isbn_bnf):
    #                     non_alignment_isbn_present += 1
    #                 else:
    #                     non_alignment_isbn_absent += 1
    #             else:
    #                 missing_isbn_bnf_in_negatives += 1
    #         elif not url_bnf and url_constellation:
    #             total_non_alignment += 1
    #             if isbn_constellation:
    #                 # look if isbn present in a bnf book
    #                 if self.is_isbn_in_alignments_bnf(isbn_constellation):
    #                     non_alignment_isbn_present += 1
    #                 else:
    #                     non_alignment_isbn_absent += 1
    #             else:
    #                 # missing isbn
    #                 missing_isbn_constellation_in_negatives += 1
    #         else:  # no url at all
    #             lines_without_url += 1
    #             self.stats_logger("empty line", book_key)
    #
    #     self.stats_logger.info(f"total alignment P {total_alignment}")
    #     self.stats_logger.info(f"total non-alignment N {total_non_alignment}")
    #     self.stats_logger.info(f"lines without url {lines_without_url}")
    #     self.stats_logger.info(f"alignment & isbn matches TP {isbn_equality}")
    #     self.stats_logger.info(f"alignment & NOT isbn matches FP {isbn_inequality}")
    #     self.stats_logger.info(f"NON alignment & NON isbn present TN {non_alignment_isbn_absent}")
    #     self.stats_logger.info(f"NON alignment & isbn present FN {non_alignment_isbn_present}")
    #     self.stats_logger.info(f"missing isbn bnf for positives {missing_isbn_bnf_in_positives}")
    #     self.stats_logger.info(f"missing isbn constellation for positives {missing_isbn_constellation_in_positives}")
    #     self.stats_logger.info(f"missing isbn bnf for negatives {missing_isbn_bnf_in_negatives}")
    #     self.stats_logger.info(f"missing isbn constellation for negatives {missing_isbn_constellation_in_negatives}")


    def output_csv(self):
        with open(f"exact_alignment_{self.key_type}.csv", "w", encoding='utf-8', newline="") as csvfile:
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
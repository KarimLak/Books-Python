import utils
import csv

from book_alignment import BookAlignment
from interdbstats import InterDbStats


class InterDbStatsExact(InterDbStats):
    def __init__(self, key_type, stats_logger) -> None:
        super().__init__(key_type, stats_logger)
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.alignment_method = "exact"


    def align_btlf(self, book_data, book_key):
        if book_key in self.all_book_alignments:
            self.all_book_alignments[book_key].align_btlf(isbn_btlf=book_data.isbn,
                                                          uri_btlf=book_data.uri,
                                                          age_range_btlf=book_data.age_range_int)
    def align_by_key(self, book_alignment:BookAlignment, book_key):  # O(1)
        if book_key in self.all_book_alignments:
            if not self.all_book_alignments[book_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[book_key].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                             ean_bnf=book_alignment.ean_bnf,
                                                             url_bnf=book_alignment.url_bnf,
                                                             uri_bnf=book_alignment.uri_bnf,
                                                             age_range_bnf=book_alignment.age_range_bnf)
                self.increment_alignment_number()

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf


        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    def align_by_ean_isbn(self, book_alignment:BookAlignment, isbn_bnf, ean_bnf):  # O(1)
        if isbn_bnf in self.all_book_alignments:
            if not self.all_book_alignments[isbn_bnf].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[isbn_bnf].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                             ean_bnf = book_alignment.ean_bnf,
                                                             url_bnf=book_alignment.url_bnf,
                                                             uri_bnf=book_alignment.uri_bnf,
                                                             age_range_bnf=book_alignment.age_range_bnf,
                                                             ean_used_to_align=False)
                self.increment_alignment_number()

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf

        elif ean_bnf in self.all_book_alignments:
            if not self.all_book_alignments[ean_bnf].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[ean_bnf].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                             ean_bnf=book_alignment.ean_bnf,
                                                             url_bnf=book_alignment.url_bnf,
                                                             uri_bnf=book_alignment.uri_bnf,
                                                             age_range_bnf=book_alignment.age_range_bnf,
                                                            ean_used_to_align=True)
                self.increment_alignment_number()
            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf

        else:
            self.all_book_alignments[isbn_bnf] = book_alignment  # bnf data gets into the dict without alignment


    def output_csv_constellation_bnf(self):
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


    def output_csv_constellation_bnf_btlf(self):
        with open(f"exact_alignment_{self.key_type}.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow(["key",
                             "isbn_constellation",
                             "isbn_bnf",
                             "isbn_btlf",
                             "age_range_constellation",
                             "age_range_bnf",
                             "age_range_btlf",
                             "url_constellation",
                             "url_bnf",
                             "uri_btlf"])
            for key in self.all_book_alignments.keys():
                book_alignment_output = self.all_book_alignments[key]
                writer.writerow([key,
                                 book_alignment_output.isbn_constellation,
                                 book_alignment_output.isbn_bnf,
                                 book_alignment_output.isbn_btlf,
                                 book_alignment_output.age_range_constellation,
                                 book_alignment_output.age_range_bnf,
                                 book_alignment_output.age_range_btlf,
                                 book_alignment_output.url_constellation,
                                 book_alignment_output.url_bnf,
                                 book_alignment_output.uri_btlf])
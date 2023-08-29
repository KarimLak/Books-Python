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
                                                             url_bnf=book_alignment.url_bnf,
                                                             uri_bnf=book_alignment.uri_bnf)
                self.increment_alignment_number()

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf


        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

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

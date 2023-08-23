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
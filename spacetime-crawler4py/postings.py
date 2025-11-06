class Posting:
    def __init__(self):
        self.posting = {}

    def add_entry(self, docID, tfidf, fields):
        self.posting[docID] = tfidf

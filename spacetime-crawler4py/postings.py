class Posting:
    def __init__(self):
        self.posting = {}

    def add_entry(self, docID, tfidf):
        self.posting[docID] = tfidf

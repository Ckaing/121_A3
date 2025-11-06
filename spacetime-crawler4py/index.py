from postings import Posting


class Index:
    def __init__(self):
        self.index = {}

    def add_token(self, token):
        if (token not in self.index):
            self.index[token] = Posting()

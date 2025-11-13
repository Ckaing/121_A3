class Posting:
    def __init__(self):
        self.freq = 0
        self.fields = []
        self.position = []

    def add_entry(self, freq: int, fields, positions):
        # change freq to tfidf later
        self.freq = freq
        self.fields = fields
        self.position = positions


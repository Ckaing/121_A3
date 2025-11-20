class Posting:
    def __init__(self):
        self.freq = 0
        self.fields = []
        self.position = []

    def add_entry(self, freq, fields, positions=None):
        # change freq to tfidf later
        self.freq = freq
        self.fields = fields
        self.position = positions

    def merge(self, freq, fields):
        self.freq += freq
        self.fields += fields

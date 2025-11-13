class Posting:
    def __init__(self):
        self.posting = {}
        self.fields = {}
        self.position = {}

    def add_entry(self, docID, freq, fields : str[], positions : int[]):
        self.posting[docID] = freq
        self.fields[docID] = fields
        self.position[docID] = positions

    def __str__(self) -> str:
        post = []
        for id, freq in self.posting.items():
            post.append(f"{id}-{freq}")
        return " ".join(post)

class Posting:
    def __init__(self):
        self.posting = {}

    def add_entry(self, docID, tfidf):
        self.posting[docID] = tfidf

    def __str__(self) -> str:
        post = []
        for id, freq in self.posting.items():
            post.append(f"({id},{freq})")
        return " ".join(post)

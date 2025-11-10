from postings import Posting


class Index:
    def __init__(self):
        self.index = {}

    def add_entry(self, token):
        if (token not in self.index):
            self.index[token] = Posting()

    def write_to_file(self, file):
        with open(file,"w") as outfile:
            for url, id in enumerate(self.index):
                print(f"{id} - {url}", file=outfile)
        self._reset()

    def _reset(self):
        self.index = {}


class URLIndex(Index):
    def __init__(self):
        super().__init__()
        self.count = 1

    def add_entry(self, url):
        if (url not in self.index.keys()):
            self.index[url] = self.count
            self.count += 1

    def get_id(self, url):
        return self.index[url]

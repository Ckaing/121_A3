from postings import Posting


class Index:
    def __init__(self):
        self.index = {}

    def add_entry(self, token):
        if (token not in self.index):
            self.index[token] = Posting()

    def add_posting(self, token, urlid, freq):
        if (token not in self.index):
            print("Token not in index. Failed to add frequency.")
            return
        post = self.index[token]
        post.add_entry(urlid, freq)

    def write_to_file(self, file):
        with open(file, "w") as outfile:
            for i, (token, post) in enumerate(self.index.items()):
                print(f"{token} -> {post}", file=outfile)
        self._reset()

    def _reset(self):
        self.index = {}

    def fill_index(self, file):
        if len(self.index) > 0:
            self._reset()
        with open(file, "r") as infile:
            # each line is in the format [token] -> id-freq id-freq id-freq
            for line in infile:
                # split line to separate the token and postings
                lines = line.split(" -> ")
                self.add_entry(lines[0])
                # split the postings to get the info
                posts = lines[1].split()
                for p in posts:
                    entry = p.split('-')
                    self.add_posting(lines[0], entry[0], entry[1])


class URLIndex(Index):
    def __init__(self):
        super().__init__()
        self.count = 1

    def add_entry(self, url):
        if (url not in self.index.values()):
            self.index[self.count] = url
            self.count += 1

    def get_id(self, url):
        return self.index[url]

    def length(self):
        return self.count

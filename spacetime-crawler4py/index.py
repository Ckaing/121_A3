from postings import Posting


class Index:
    def __init__(self):
        self.index = {}

    def add_entry(self, token):
        """Initializes token into self.index with a Posting object
        if not already initialized."""
        if (token not in self.index):
            self.index[token] = Posting()

    def add_posting(self, token, urlid, freq):
        """Adds entry into the Posting object associated with token, using
        the docID and token frequency in that docID."""
        if (token not in self.index):
            print("Token not in index. Failed to add frequency.")
            return
        post = self.index[token]
        post.add_entry(urlid, freq)

    def write_to_file(self, file):
        """Writes the information in self.index into a file. Clears index
        for next batch to be read in."""
        with open(file, "w") as outfile:
            for i, (token, post) in enumerate(self.index.items()):
                print(f"{token} -> {post}", file=outfile)
        self._reset()

    def _reset(self):
        """Private function that will clear the index of all its entries
        so it can be used for the next batch of urls that are processed."""
        self.index = {}

    def fill_index(self, file):
        """Reads from file and inputs each entry into the index. Resets
        index before reading if index is already filled."""
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
        self.id = 1

    def add_entry(self, url):
        """Adds a url to the index if not already in the list.
        There is a unique ID for every url."""
        if (url not in self.index.values()):
            self.index[self.id] = url
            self.id += 1

    def get_url(self, id):
        """Returns url associated with id."""
        return self.index[id]

    def length(self):
        """Returns number of index documents with unique ids."""
        return self.id

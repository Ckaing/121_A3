from postings import Posting


class Index:
    def __init__(self):
        self.index = {}

    def add_token(self, token):
        """Initializes token into self.index with a Posting object
        if not already initialized."""
        if (token not in self.index):
            self.index[token] = {}

    def add_posting(self, token, docid):
        """Adds Posting obj to specified token with associated docID."""
        if (token not in self.index):
            self.index[token] = {}
        if (docid not in self.index[token].keys()):
            self.index[token][docid] = Posting()

    def write_to_file(self, file):
        """Writes the information in self.index into a file. Clears index
        for next batch to be read in."""
        #write here and reset after
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
        # read back into the object here
    
    # TODO: write this function similar to fill_index but with additional
    # checks for whether it is already in the index. Idk if we want to write
    # it back to file at the end but I was thinking that we merge after every
    # batch of urls we parse.
    def merge(self, file):
        """Read from file and merges the tokens we read with the tokes in memory"""


class URLIndex:
    def __init__(self):
        self.index = {}
        self.id = 1

    def add_entry(self, url):
        """Adds a url to the index if not already in the list.
        There is a unique ID for every url."""
        if (url not in self.index.values()):
            self.index[self.id] = url
            self.id += 1

    def get_url(self, id) -> str:
        """Returns url associated with id."""
        return self.index[id]

    def length(self) -> int:
        """Returns number of index documents with unique ids."""
        return self.id

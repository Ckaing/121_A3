from postings import Posting
import json

def custom_encoder(obj):
    if isinstance(obj, Posting):
        return {
            'freq': obj.freq,
            'fields': obj.fields,
            'position': obj.position
        }
    raise TypeError("Object of type %s is not JSON serializable" % type(obj).__name__)

def custom_decoder(dct):
    if 'freq' in dct and 'fields' in dct and 'position' in dct:
        post = Posting()
        post.freq = dct['freq']
        post.fields = dct['fields']
        post.position = dct['position']
        return post
    return dct

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
        """Writes the information in self.index into a json file. Clears index
        for next batch to be read in."""
        with open(file, "w") as outfile:
            outfile.write(json.dumps(self.index, default=custom_encoder))
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
    
    # TODO: write this function similar to fill_index but with additional
    # checks for whether it is already in the index. Idk if we want to write
    # it back to file at the end but I was thinking that we merge after every
    # batch of urls we parse.
    def merge(self, file):
        """Read from file. If the token is in the current index, add the
        postings from the token to current index. If token not in current
        index, add token."""


class URLIndex(Index):
    def __init__(self):
        super().__init__()
        self.id = 1

    def add_entry(self, url):
        """Adds a url to the index if not already in the list.
        There is a unique ID for every url."""
        if (url not in self.index.values()):
            self.id += 1
            self.index[self.id] = url

    def get_url(self, id) -> str:
        """Returns url associated with id."""
        return self.index[id]

    def length(self) -> int:
        """Returns number of index documents with unique ids."""
        return self.id
    
    def get_id(self, url) -> int:
        """Returns the id associated with the url."""
        ids = [id for id, val in self.index.items() if val == url]
        if (len(ids) == 1):
            return ids[0]
        else:
            raise Exception(IndexError, f"{url} not found in URL Index\n")
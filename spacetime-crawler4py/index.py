from postings import Posting
import json

def custom_encoder(obj):
    """Encodes Posting objects into a dictionary for JSON serialization."""
    if isinstance(obj, Posting):
        return {
            'freq': obj.freq,
            'fields': obj.fields,
            'position': obj.position
        }
    raise TypeError("Object of type %s is not JSON serializable" % type(obj).__name__)

def custom_decoder(dct):
    """Decodes a dictionary into a Posting object if applicable."""
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

    def add_posting(self, token, docid, freq, fields, position=None): # Temporary fields and position to None for testing
        """Adds Posting obj to specified token with associated docID."""
        if (token not in self.index):
            self.index[token] = {}
        if (docid not in self.index[token].keys()):
            self.index[token][docid] = Posting()
            self.index[token][docid].add_entry(freq, fields, position)

    def write_to_file(self, file):
        """Sorts the index by the tokens. Writes the information in self.index
        into a json file. Clears index for next batch to be read in."""
        with open(file, "w") as outfile:
            outfile.write(json.dumps(dict(sorted(self.index.items())), default=custom_encoder))
        self._reset()

    def _reset(self):
        """Private function that will clear the index of all its entries
        so it can be used for the next batch of urls that are processed."""
        self.index = {}
    
    # TODO:
    # checks for whether token is already in the index and check if id in the token's
    # dictionary and if not, then add an entry. sort at the very end.
    def merge(self, file):
        """Read from file. If the token is in the current index, add the
        postings from the token to current index. If token not in current
        index, add token."""


class URLIndex(Index):
    def __init__(self):
        super().__init__()
        self.id = 0

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
from postings import Posting
import json
import string

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

        for letter in string.ascii_lowercase:
            self.index[letter] = {}
        self.index["0-9"] = {}

    def _get_dict_bucket(self, word):
        first_char = word[0].lower()
        if first_char >= 'a' and first_char <= 'z':
            return first_char
        else:
            return "0-9"
        
    def _get_bucket_file(self, letter):
        """Returns the file name for the bucket"""
        return f"index/{letter}"

    def add_entry(self, token, docid, freq, fields, position=None):
        """Initializes token into self.index[bucket] with a Posting object
        if not already initialized."""
        bucket = self._get_dict_bucket(token)
        # ensure token is in the bucket, adds if not
        if token not in self.index[bucket]:
            self.index[bucket][token] = {}
            
        # ensures docid is in token dict, initializes if not
        if docid not in self.index[bucket][token]:
            self.index[bucket][token][docid] = Posting()

        # add to the posting of the docid for the token
        self.index[bucket][token][docid].add_entry(freq, fields, position)

    def _reset(self):
        """Private function that will clear the index of all its entries
        so it can be used for the next batch of urls that are processed."""
        for letter in self.index:
            self.index[letter] = {}

    def write_to_file(self):
        """Iterates each bucket. Opens the file for that bucket. Loads data from file.
        Merge the current data with the data loaded. Write back to file. Reset index at the end"""
        for letter in self.index:
            file = self._get_bucket_file(letter)
            with open(file, "w+") as outfile:
                partial_data = json.load(outfile)
                for term, posting in self.index[letter].items():
                    if term not in partial_data:
                        partial_data[term] = {}
                    for id, post in posting.items():
                        if id not in partial_data[term]:
                            partial_data[term][id] = Posting()
                        partial_data[term][id].add_entry(post.freq, post.fields, post.position)
                outfile.write(json.dumps(dict(sorted(partial_data.items())), default=custom_encoder))
        self._reset()


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
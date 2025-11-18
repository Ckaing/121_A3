from postings import Posting
import json
import string
import os

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


class BatchIndexer:
    """
    Build inverted index with bucketing from the start.
    Each batch creates bucketed partial indexes.
    Final merge combines all partial indexes into one JSON file per bucket.
    """
    
    def __init__(self, output_dir='index_output', temp_dir='index_temp'):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.bucket_keys = list(string.ascii_lowercase) + ['0-9']
        
        # Create directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Track partial index files for each bucket
        self.partial_files = {bucket: [] for bucket in self.bucket_keys}
        self.batch_count = 0
        
        # Current batch index (accumulates documents until save_batch_to_disk)
        self.current_batch = self._initialize_bucketed_index()
    
    def _get_bucket_key(self, term):
        """Return which bucket a term belongs to"""
        if not term:
            return '0-9'
        first_char = term[0].lower()
        return first_char if first_char.isalpha() else '0-9'
    
    def _initialize_bucketed_index(self):
        """Create empty bucketed structure"""
        return {bucket: {} for bucket in self.bucket_keys}
    
    def add_document(self, doc_id, term, freq, fields):
        """Add a single document to the current batched index."""
        bucket_key = self._get_bucket_key(term)
        
        if term not in self.current_batch[bucket_key]:
            self.current_batch[bucket_key][term] = {}
        
        self.current_batch[bucket_key][term][doc_id] = {
            'term_frequency': freq,
            'fields': fields.copy()
        }
    
    def save_batch_to_disk(self):
        """Save current batch to disk as partial files."""
        for bucket_key, bucket_data in self.current_batch.items():
            if not bucket_data:  # Skip empty buckets
                continue
            
            # Create filename for this bucket's partial index
            filename = f'bucket_{bucket_key}_batch_{self.batch_count}.json'
            filepath = os.path.join(self.temp_dir, filename)
            
            # Save to disk
            with open(filepath, 'w') as f:
                json.dump(bucket_data, f, indent=2)
            
            # Track this partial file
            self.partial_files[bucket_key].append(filepath)
        
        self.batch_count += 1
        
        # Reset current batch
        self.current_batch = self._initialize_bucketed_index()
    
    def merge_bucket_files(self, bucket_key):
        """Merge all partial files for a single bucket."""
        merged_bucket = {}
        partial_files = self.partial_files[bucket_key]
        
        print(f"Merging {len(partial_files)} partial files for bucket '{bucket_key}'...")
        
        for filepath in partial_files:
            # Load partial index
            with open(filepath, 'r') as f:
                partial_data = json.load(f)
            
            # Merge into final bucket
            for term, doc_postings in partial_data.items():
                if term not in merged_bucket:
                    merged_bucket[term] = {}
                
                # Merge document postings
                for doc_id, posting in doc_postings.items():
                    if doc_id not in merged_bucket[term]:
                        merged_bucket[term][doc_id] = {
                            'term_frequency': posting['term_frequency'],
                            'fields': posting['fields'].copy()
                        }
                    else:
                        # Merge with existing (in case same doc appears in multiple batches)
                        existing = merged_bucket[term][doc_id]
                        existing['term_frequency'] += posting['term_frequency']
                        existing['fields'].extend(posting['fields'])
        
        return merged_bucket
    
    def merge_all_buckets(self, cleanup_temp=True):
        """Merge all partial files into final bucket JSON files."""
        print(f"\nMerging all buckets from {self.batch_count} batches...")
        
        for bucket_key in self.bucket_keys:
            if not self.partial_files[bucket_key]:
                print(f"Bucket '{bucket_key}': No data (skipped)")
                continue
            
            # Merge all partial files for this bucket
            merged_bucket = self.merge_bucket_files(bucket_key)
            
            # Save final bucket file
            output_file = os.path.join(self.output_dir, f'bucket_{bucket_key}.json')
            with open(output_file, 'w') as f:
                json.dump(merged_bucket, f)
            
            print(f"Bucket '{bucket_key}': {len(merged_bucket)} terms -> {output_file}")
        
        # Cleanup temporary files
        if cleanup_temp:
            self._cleanup_temp_files()
        
        print(f"\nAll buckets merged successfully!")
    
    def _cleanup_temp_files(self):
        """Remove temporary partial index files"""
        print("Cleaning up temporary files...")
        for bucket_key, file_list in self.partial_files.items():
            for filepath in file_list:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        # Remove temp directory if empty
        if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def get_final_stats(self):
        """Get statistics about final buckets"""
        stats = {}
        for bucket_key in self.bucket_keys:
            filepath = os.path.join(self.output_dir, f'bucket_{bucket_key}.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                stats[bucket_key] = {
                    'terms': len(data),
                    'file_size_mb': os.path.getsize(filepath) / (1024 * 1024)
                }
        return stats


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
            with open(file, "r+") as outfile:
                partial_data = json.load(outfile, object_hook=custom_decoder)
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
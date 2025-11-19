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
    
    def __init__(self, output_dir='main_index', temp_dir='temp'):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.bucket_keys = list(string.ascii_lowercase) + ['0-9']
        
        # create directories for the index
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # track partial index files for each bucket
        self.partial_files = {bucket: [] for bucket in self.bucket_keys}
        self.batch_count = 0
        
        # current batch's index
        self.current_batch = self._initialize_bucketed_index()
    
    def _get_bucket_key(self, token):
        """Return which bucket a token belongs to"""
        # if not token:
        #     return '0-9'
        first_char = token[0].lower()
        return first_char if first_char.isalpha() else '0-9'
    
    def get_bucket_filename(self, token):
        """Return the name of the file associated with the token."""
        bucket = self._get_bucket_key(token)
        return f"./main_index/bucket_{bucket}.json"
    
    def _initialize_bucketed_index(self):
        """Create empty bucketed structure"""
        return {bucket: {} for bucket in self.bucket_keys}
    
    def add_document(self, doc_id, token, freq, fields):
        """Add a single document to the current batched index."""
        bucket_key = self._get_bucket_key(token)
        
        if token not in self.current_batch[bucket_key]:
            self.current_batch[bucket_key][token] = {}
        
        self.current_batch[bucket_key][token][doc_id] = Posting()
        self.current_batch[bucket_key][token][doc_id].add_entry(freq, fields)
    
    def save_batch_to_disk(self):
        """Save current batch to disk as partial files."""
        for bucket_key, bucket_data in self.current_batch.items():
            # skip empty buckets
            if not bucket_data:
                continue
            
            # create filename for this bucket's partial index
            filename = f'bucket_{bucket_key}_batch_{self.batch_count}.json'
            filepath = os.path.join(self.temp_dir, filename)
            
            # save to disk
            with open(filepath, 'w') as f:
                json.dump(bucket_data, f, indent=2, default=custom_encoder)
            
            # track this partial file
            self.partial_files[bucket_key].append(filepath)
        
        self.batch_count += 1
        
        # reset current batch
        self.current_batch = self._initialize_bucketed_index()
    
    def merge_bucket_files(self, bucket_key):
        """Merge all partial files for a single bucket."""
        merged_bucket = {}
        partial_files = self.partial_files[bucket_key]
        
        print(f"Merging {len(partial_files)} partial files for bucket '{bucket_key}'...")
        
        for filepath in partial_files:
            # Load partial index
            with open(filepath, 'r') as f:
                partial_data = json.load(f, object_hook=custom_decoder)
            
            # Merge into final bucket
            for token, doc_postings in partial_data.items():
                if token not in merged_bucket:
                    merged_bucket[token] = {}
                
                # Merge document postings
                for doc_id, posting in doc_postings.items():
                    if doc_id not in merged_bucket[token]:
                        merged_bucket[token][doc_id] = Posting()
                        merged_bucket[token][doc_id].add_entry(posting.freq, posting.fields.copy())
                    else:
                        # Merge with existing (in case same doc appears in multiple batches)
                        existing = merged_bucket[token][doc_id]
                        existing.merge(posting.freq, posting.fields)
        
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
                json.dump(dict(sorted(merged_bucket.items())), f, default=custom_encoder)
            
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
        
        # remove temp directory if empty
        if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def get_final_stats(self):
        """Get statistics about final buckets"""
        stats = {}
        for bucket_key in self.bucket_keys:
            filepath = os.path.join(self.output_dir, f'bucket_{bucket_key}.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f, object_hook=custom_decoder)
                stats[bucket_key] = {
                    'terms': len(data),
                    'file_size_mb': os.path.getsize(filepath) / (1024 * 1024)
                }
        return stats


class URLIndex:
    def __init__(self):
        self.index = {}
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
        
    def write_to_file(self, file):
        with open(file, "w") as outfile:
            json.dump(dict(sorted(self.index.items())), outfile, default=custom_encoder)
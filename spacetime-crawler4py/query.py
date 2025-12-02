from tokenizer import stemmer
# pip install orjson
import orjson
import math
import string
from collections import OrderedDict
import heapq
import time


class Query:
    
    def __init__(self, max_cache=5) -> None:
        with open("url_id_index.json", 'r') as f:
            self.url_mapping = orjson.loads(f.read())
        self.idf_cache = {}
        self.bucket_cache = OrderedDict()
        self.total_docs = len(self.url_mapping)
        self.max_cached_buckets = max_cache
        self._compute_idf()
    
    def _get_bucket_key(self, word):
        first_char = word[0].lower()
        if not first_char.isalpha():
            first_char = '0-9'
        return first_char
    
    def _load_bucket_to_cache(self, letter: str):
        if letter in self.bucket_cache:
            self.bucket_cache.move_to_end(letter)
            return self.bucket_cache[letter]

        if len(self.bucket_cache) > self.max_cached_buckets:
            self.bucket_cache.popitem(last=False)

        json_file_path = f"main_index/bucket_{letter}.json"
        with open(json_file_path, 'r') as f:
            bucket = orjson.loads(f.read())
        
        self.bucket_cache[letter] = bucket
        self.bucket_cache.move_to_end(letter)
        return bucket
        
    def _compute_idf(self):
        for letter in string.ascii_lowercase:
            print(letter)
            json_file_path = f"main_index/bucket_{letter}.json"

            with open(json_file_path, 'r') as f:
                index = orjson.loads(f.read())
            
            for term, posting in index.items():
                doc_freq = len(posting)  # Number of docs containing this term
                self.idf_cache[term] = math.log10(self.total_docs / doc_freq) if doc_freq > 0 else 0
        
        json_file_path = f"main_index/bucket_0-9.json"

        with open(json_file_path, 'r') as f:
            index = orjson.loads(f.read())
        
        for term, posting in index.items():
            doc_freq = len(posting)  # Number of docs containing this term
            self.idf_cache[term] = math.log10(self.total_docs / doc_freq) if doc_freq > 0 else 0

    def user_input(self):
        """Gets the user input from the query."""
        # will be changed later but for now after implementing GUI
        return input("Enter query:\n")

    def _extract_terms(self, user_input: str):
        """Given the user input, separate the terms and return a list of them."""
        import re
        # uses same splitting method as tokenizer
        tokens = re.findall(r'\b[a-z0-9]{3,}\b', user_input.lower())

        return tokens

    def query(self, q):
        """Given a list of terms, check respective files for the token and
        then return the postings for each token and check intersections of
        the postings. Returns the top 5 urls."""

        terms = self._extract_terms(q)
        # Stem all query terms
        stemmed_query = [stemmer.stem(term) for term in terms]

        all_postings = {}
        doc_term_count = {}
        for word in stemmed_query:
            #Impliment opening file for batches here
            bucket_key = self._get_bucket_key(word)
            bucket = self._load_bucket_to_cache(bucket_key)
            if word not in bucket:
                continue
            
            idf = self.idf_cache.get(word, 0)
            
            for docid, posting_data in bucket[word].items():
                tf = posting_data.get('freq', 0)  # Term frequency in document
                fields = posting_data.get('fields') or []
                
                # TF-IDF score
                score = (1 + math.log10(tf)) * idf if tf > 0 else 0
                
                # Boost for important fields (titles, headers)
                if fields and 'important' in fields:
                    score *= 2.5  # Stronger boost for important content
                
                # Accumulate scores for documents
                all_postings[docid] = all_postings.get(docid, 0) + score
                doc_term_count[docid] = doc_term_count.get(docid, 0) + 1
        
        # Boost documents that match multiple query terms
        if len(stemmed_query) > 1:
            for docid in all_postings:
                # Count how many query terms appear in this document
                terms_matched = doc_term_count.get(docid, 0)
                if terms_matched > 1:
                    # Give 30% boost for each additional term matched
                    all_postings[docid] *= (1 + 0.3 * (terms_matched - 1))
                if terms_matched < len(stemmed_query):
                    match_ratio = terms_matched / len(stemmed_query) # Penalty for partial matches
                    all_postings[docid] *= (0.1 + 0.4 * match_ratio) # Scale between 0.1 to 0.5

        # Sort by score (descending) and get top 5
        top_docids = heapq.nlargest(5, all_postings.items(), key=lambda x: x[1])

        # Convert docIDs to URLs with scores
        top_urls = [(self.url_mapping.get(str(docid), "URL not found"), score)
                    for docid, score in top_docids]
        return top_urls


    def print_query_results(self, top_urls):
        """Prints the query results in a readable format."""
        print("Top URLs for your query:")
        for url, score in top_urls:
            print(f"URL: {url} | Score: {score:.4f}")


process_query = Query()
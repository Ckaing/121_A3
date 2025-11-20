from tokenizer import tokenize, stemmer
import json
import math

def token_file(token):
    """Returns the file name that the token might be found in."""
    return f"index/{token[0]}"


def user_input():
    """Gets the user input from the query."""
    # will be changed later but for now after implementing GUI
    return input("Enter query:\n")


def extract_terms(user_input: str):
    """Given the user input, separate the terms and return a list of them."""
    import re
    # uses same splitting method as tokenizer
    tokens = re.findall(r'\b[a-z0-9]{3,}\b', user_input.lower())

    return tokens


def query(q):
    """Given a list of terms, check respective files for the token and
    then return the postings for each token and check intersections of
    the postings. Returns the top 5 urls."""

    # Stem all query terms
    stemmed_query = [stemmer.stem(term) for term in q]
    
    # Load URL mapping
    with open("url_id_index.json", 'r') as f:
        url_mapping = json.load(f)

    total_docs = len(url_mapping)
    all_postings = {}
    doc_term_count = {}

    for word in stemmed_query:
        #Impliment opening file for batches here
        first_char = word[0].lower()
        if not first_char.isalpha():
            first_char = '0-9'

        json_file_path = "main_index/bucket_" + first_char + ".json"

        with open(json_file_path, 'r') as f:
            index = json.load(f)

        
        if word in index:
            # Calculate IDF: log(total_docs / docs_containing_term)
            doc_freq = len(index[word])  # Number of docs containing this term
            idf = math.log10(total_docs / doc_freq) if doc_freq > 0 else 0
            
            for docid, posting_data in index[word].items():
                tf = posting_data.get('freq', 0)  # Term frequency in document
                fields = posting_data.get('fields') or []
                
                # TF-IDF score
                score = (1 + math.log10(tf)) * idf if tf > 0 else 0
                
                # Boost for important fields (titles, headers)
                if fields and 'important' in fields:
                    score *= 2.5  # Stronger boost for important content
                
                # Accumulate scores for documents
                if docid in all_postings:
                    all_postings[docid] += score
                else:
                    all_postings[docid] = score
                
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
    top_docids = sorted(all_postings.items(), 
                       key=lambda x: x[1], 
                       reverse=True)[:5]
    
    # Convert docIDs to URLs with scores
    top_urls = []
    for docid, score in top_docids:
        url = url_mapping.get(str(docid), "URL not found")
        top_urls.append((url, score))
    
    return top_urls


def print_query_results(top_urls):
    """Prints the query results in a readable format."""
    print("Top URLs for your query:")
    for url, score in top_urls:
        print(f"URL: {url} | Score: {score:.4f}")
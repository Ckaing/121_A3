from tokenizer import tokenize, stemmer

def token_file(token):
    """Returns the file name that the token might be found in."""
    return f"index/{token[0]}"


def user_input():
    """Gets the user input from the query."""
    # will be changed later but for now after implementing GUI
    return input("Enter query: ")


def extract_terms(input: str):
    """Given the user input, separate the terms and return a list of them."""
    return input.split(" AND ")


def query(q):
    """Given a list of terms, check respective files for the token and
    then return the postings for each token and check intersections of
    the postings. Returns the top 5 urls."""
    len_q = len(q)
    # replace the words in q with its stem
    for i in range(len_q):
        q[i] = stemmer.stem(q[i])

    # each element is a list of docids for each term
    postings = []
    for word in q:
        # get the file name of where the token would be
        file = token_file(word)
        # open the file, retrieve index, find token and insert the keys
        # (docid) into postings
    
    # save the top urls
    urls = []
    # search the postings for matching documents
    
    return urls
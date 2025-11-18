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
    
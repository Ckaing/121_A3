from index import Posting, URLIndex, Index
from stemmer import Stemmer


stemmer = Stemmer()


def compute_text_frequencies(text):
    """
    Description: Streamlines the computation from text to frequency dictionary

    Input: The string to convert into a frequency dictionary
    Output: The resulting dictionary
    """
    tokens = tokenize(text)
    if tokens is not None:
        freq = compute_word_frequencies(tokens)
        return len(tokens), freq
    else:
        print('Please resolve the error and try again.')
        return None


def tokenize(content):
    """
    Description: Breaks content down into tokens

    Input: The string to tokenize
    Output: A list of tokens
    """
    tokens = []
    word = ''

    # remove case sensitivity
    content = content.lower()

    for c in content:
        if 'a' <= c and c <= 'z': 
            word += c
        else:
            if len(word) > 2:
                tokens.append(word)
            word = ''

    if len(word) > 2:
        tokens.append(word)

    return tokens


def compute_word_frequencies(tokens):
    """
    Description: Turns list of tokens into a dictionary of counts for 
    each unique token.

    Input: A list of tokens
    Output: The dictionary of frequency counts for each unique token
    """
    freq = {}
    for token in tokens:
        word = stemmer.stem(token)
        if word not in freq:
            freq[word] = 0
        freq[word] += 1
    return freq


def union_freq(freq1, freq2):
    """
    Description: Combines two dictionaries of frequency counts into one

    Input: Two frequency dictionaries
    Output: One dicionary containing the combined result
    """
    result = {}
    for key in freq1.keys() | freq2.keys(): 
        result[key] = freq1.get(key, 0) + freq2.get(key, 0)
    return result

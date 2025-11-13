from index import Index, URLIndex
from postings import Posting
from bs4 import BeautifulSoup
import tokenizer

index = Index()
urls = URLIndex()

def indexer(url, html_content):
    """Input: list of url documents"""
    if (url not in urls.values()):
        urls.add_entry(url)
        docID = urls.length() - 1
    
    docID = urls.get_id(url)
    # create new function using porter stemming algorithm to stem words
    # update tokenizer to use porter stemming algo
    soup = BeautifulSoup(html_content, "lxml")
    text = soup.get_text(separator=' ', strip=True)
    word_count, freq = tokenizer.compute_text_frequencies(text)
    # extract fields of the tokens in tokenizer
    for token in word_count: 
        fields = []
        for element in soup.find_all(['h1','h2','h3', 'title', 'strong']):
            if token in element.get_text():
                fields.append(element.name)
        index.add_posting(token, docID, freq[token], fields, []) #empty pos list for now
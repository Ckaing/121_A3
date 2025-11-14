from index import Index, URLIndex
from postings import Posting
from bs4 import BeautifulSoup
import tokenizer

index = Index()
urls = URLIndex()

def indexer(url, html_content):
    """Given a single url and html_content from the url, update
    the global Index variables above. Only viable for small set
    of documents."""
    if (url not in urls.values()):
        urls.add_entry(url)
        docID = urls.length() - 1
    else:
        docID = urls.get_id(url)
    soup = BeautifulSoup(html_content, "lxml")
    text = soup.get_text(separator=' ', strip=True)
    word_count, freq = tokenizer.compute_text_frequencies(text)
    # keep word count to help calc tf-idf later
    # extract fields of the tokens in tokenizer
    for token in freq: 
        fields = [element.name for element in soup.find_all(['h1', 'h2', 'h3', 'title', 'strong'])
                  if token in element.get_text()]
        index.add_posting(token, docID, freq[token], fields, [])

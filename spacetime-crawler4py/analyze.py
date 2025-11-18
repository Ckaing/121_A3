from urllib.parse import urldefrag, urlparse
from bs4 import BeautifulSoup
from index_vars import json_index, URL_id_index, url_index_lock, json_index_lock
from threading import Lock
import os

import tokenizer



# globals for analysis
unique_pages = set()
word_freq = {}
word_freq_lock = Lock()


def get_file_size_in_kb(file_path):
    """
    Returns the size of a file in kilobytes.
    """
    if os.path.exists(file_path):
        file_size_bytes = os.path.getsize(file_path)
        file_size_kb = file_size_bytes / 1024
        return file_size_kb
    else:
        return None

def analysis(url, html_content):
    """
    Description: Analyzes a page for the report, updating global values
    unique_pages, word_freq, and json_index.

    Input: The url of the page that we are analyzing and its content
    Output: None; updates global parameters
    """
    global word_freq, unique_pages

    # defragment URL
    url, _ = urldefrag(url)
    unique_pages.add(url)

    # Add url to URL index while protected
    with url_index_lock:
        URL_id_index.add_entry(url)
        doc_id = URL_id_index.get_id(url)

    soup = BeautifulSoup(html_content, 'html.parser')

    # do analysis
    text = soup.get_text(separator=' ', strip=True)
    _ , freq = tokenizer.compute_text_frequencies(text)

    # update word frequencies with lock
    with word_freq_lock:
        word_freq = tokenizer.union_freq(word_freq, freq)

    # update inverted index with lock
    with json_index_lock:
        important_text = set()
        for tag in soup.find_all(['h1', 'h2', 'h3', 'title', 'strong']):
            tag_tokens = tokenizer.tokenize(tag.get_text())
            important_text.update(tag_tokens)

        for token, count in freq.items():
            fields = ['important'] if token in important_text else []
            json_index.add_posting(token, doc_id, count, fields)




def write_analysis_to_file(file_name='report.txt'):
    """
    Description: Writes the global report parameters into a file for us
    to reference after execution

    Input: The file name to write to, defaulted to report.txt
    Output: None; prints to file
    """
    global word_freq, unique_pages

    with open(file_name, 'w', encoding='utf-8') as report:
        print("INVERTED INDEX RESULTS", file=report)
        print("-" * 40, file=report)
        print(file=report)

        # Q1 Number of indexed documents
        print(f"Number of indexed documents: {URL_id_index.id}", file=report)

        # Q2 Number of unique tokens
        print(f"Number of unique tokens: {len(word_freq)}", file=report)

        # Q3 Size of index on disk
        index_size_kb = get_file_size_in_kb('./inverted_index.json')
        if index_size_kb is not None:
            print(f"Size of index on disk: {index_size_kb:.2f} KB", file=report)
        else:
            print("Index file not found on disk.", file=report)

        print(file=report)


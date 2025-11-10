from urllib.parse import urldefrag, urlparse
from bs4 import BeautifulSoup

import tokenizer


# globals for analysis
unique_pages = set()
longest_page = 0
longest_page_url = ""
word_freq = {}
subdomains = {}

def analysis(url, html_content):
    """
    Description: Analyzes a page for the report, updating global values
    unique_pages, longest_page, longest_page_url, word_freq, subdomains, 

    Input: The url of the page that we are analyzing and its content
    Output: None; updates global parameters
    """
    global longest_page, longest_page_url, word_freq, subdomains, unique_pages

    # defragment URL
    url, _ = urldefrag(url)
    unique_pages.add(url)

    soup = BeautifulSoup(html_content, 'lxml')

    # do analysis
    text = soup.get_text(separator=' ', strip=True)
    word_count, freq = tokenizer.compute_text_frequencies(text)

    # update longest page
    if word_count > longest_page:
        longest_page = word_count
        longest_page_url = url

    # update word frequencies
    word_freq = tokenizer.union_freq(word_freq, freq)

    # update subdomains
    parsed = urlparse(url)
    if "uci.edu" in parsed.netloc:
        subdomains[parsed.netloc] = subdomains.get(parsed.netloc, 0) + 1


def write_analysis_to_file(file_name='report.txt'):
    """
    Description: Writes the global report parameters into a file for us
    to reference after execution

    Input: The file name to write to, defaulted to report.txt
    Output: None; prints to file
    """
    global longest_page, longest_page_url, word_freq, subdomains, unique_pages

    with open(file_name, 'w', encoding='utf-8') as report:
        print("CRAWLER ANALYSIS RESULTS", file=report)
        print("-" * 40, file=report)
        print(file=report)

        # Q1 Number of unique pages
        print(f"Number of unique pages crawled: {len(unique_pages)}", file=report)
        print(file=report)

        print(f"Number of total words: {len(word_freq)}", file=report)

        # Q2 Longest page
        print(f"Longest page: {longest_page} words", file=report)
        print(f"URL: {longest_page_url}", file=report)
        print(file=report)

        # Q3 Top 50 most common words
        print("Top 50 most common words:", file=report)
        print("-" * 40, file=report)
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        for i, (word, freq) in enumerate(sorted_words[:50], 1):
            print(f"{i:2d}. {word:20s} {freq:,}", file=report)
        print(file=report)

        # Q4 Subdomain distribution (sorted alphabetically)
        print("Subdomain distribution under uci.edu:", file=report)
        print("-" * 40, file=report)
        sorted_subdomains = sorted(subdomains.items())
        for subdomain, count in sorted_subdomains:
            print(f"{subdomain}, {count}", file=report)
        print(file=report)


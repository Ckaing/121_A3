import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, urldefrag
from bs4 import XMLParsedAsHTMLWarning
import warnings

from analyze import analysis
from index_vars import page_rank

# Suppress XML warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def scraper(filepath, json_dir, url_to_file_map):
    """ 
    Description: Scraper function to extract links from JSON documents

    Input: filepath to JSON file, base directory, and URL-to-filepath mapping
    Output: list of valid links (filepaths)

    """
    links = extract_next_links(filepath, json_dir, url_to_file_map)
    return [link for link in links if is_valid(link)]


def normalize_url(url):
    """
    Description: Normalize url by removing tracking params like share/utm_ 
    from the url so that we get base url, removes repeated reference to 
    nearly identical content

    Input: The url that we evaluate
    Output: Normalized url with share/utm_ removed if present
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=False)

    # Remove tracking params
    qs = {k: v for k, v in qs.items() 
          if not (k.lower() == "share" or k.lower().startswith("utm_"))}

    # Rebuild the query string
    new_query = urlencode(qs, doseq=True) if qs else ''
    normalized = parsed._replace(query=new_query)
    return normalized.geturl()

def extract_next_links(filepath, json_dir, url_to_file_map):
    """ 
    Description: extract links from a JSON file containing web page data

    Input: filepath to JSON file, base directory, and URL-to-filepath mapping
    Output: return a list with filepaths to other JSON documents
    """
    try:
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract HTML content and URL from JSON
        html_content = data.get('content', '')
        url = data.get('url')
        
        if not html_content or not url:
            return []
        
        if len(html_content) < 500:
            return []

        # do analysis
        analysis(url, html_content)

        # parse with BeautifulSoup for links
        soup = BeautifulSoup(html_content, 'html.parser')
        found_files = []
        outgoing_urls = set()

        # extract links from HTML content
        for a in soup.find_all('a', href=True):
            href = a['href']

            # Skip empty hrefs and fragments
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue

            try:
                # Convert relative URLs to absolute using the page's URL
                absolute_url = urljoin(url, href)
                
                # defragment
                absolute_url, _ = urldefrag(absolute_url)
                
                # Normalize the URL
                absolute_url = normalize_url(absolute_url)

                # add outgoing links for PR
                outgoing_urls.add(absolute_url) 
                
                # Look up the corresponding file in our mapping
                target_file = url_to_file_map.get(absolute_url)
                if target_file:
                    found_files.append(target_file)

            except Exception as e:
                continue

        page_rank.update_links(url, outgoing_urls)

        return found_files
    except Exception as e:
        return []


def is_valid(filepath):
    """
    Description: Decide whether to process this file or not
    
    Input: The filepath that we evaluate
    Output: True if we decide to process; False otherwise
    """
    try:
        # Fast path check
        if not filepath.endswith('.json'):
            return False
        
        path = Path(filepath)
        return path.exists()
    
    except Exception:
        return False
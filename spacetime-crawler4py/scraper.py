import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, urlunparse, parse_qs, urlencode, urljoin, urldefrag

from analyze import analysis



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
    qs = parse_qs(parsed.query)

    # Remove tracking params
    for key in list(qs.keys()):
        if key.lower() == "share" or key.lower().startswith("utm_"):
            qs.pop(key)

    # Rebuild the query string
    new_query = urlencode(qs, doseq=True)
    normalized = parsed._replace(query=new_query)
    return urlunparse(normalized)


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
        url = data.get('url', str(filepath))
        
        if not html_content:
            return []

        # do analysis
        analysis(url, html_content)

        # parse with BeautifulSoup for links
        soup = BeautifulSoup(html_content, 'lxml')
        found_files = []
        # extract links from HTML content
        for a in soup.find_all('a', href=True):
            href = a['href']
            try:
                # Convert relative URLs to absolute using the page's URL
                absolute_url = urljoin(url, href)
                
                # defragment
                absolute_url, _ = urldefrag(absolute_url)
                
                # Normalize the URL
                absolute_url = normalize_url(absolute_url)
                
                # Look up the corresponding file in our mapping
                if absolute_url in url_to_file_map:
                    target_file = url_to_file_map[absolute_url]
                    found_files.append(target_file)

            except Exception as e:
                continue

        return found_files
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error processing {filepath}: {e}")
        return []


def is_valid(filepath):
    """
    Description: Decide whether to process this file or not
    
    Input: The filepath that we evaluate
    Output: True if we decide to process; False otherwise
    """
    try:
        path = Path(filepath)
        
        # Must be a JSON file
        if path.suffix != '.json':
            return False
        
        # Must exist (convert to absolute path to be sure)
        if not path.exists():
            # Try as absolute path
            abs_path = path.resolve()
            if not abs_path.exists():
                return False
        
        return True
    
    except Exception as e:
        print(f"Error validating {filepath}: {e}")
        return False
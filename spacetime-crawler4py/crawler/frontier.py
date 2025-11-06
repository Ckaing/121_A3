import os
import json
import shelve
from pathlib import Path


from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        # multithreading
        # initialize lock to prevent race conditions on shared resource
        self.lock = RLock() 

        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()

        # Build URL to file mapping
        self.url_to_file_map = {}
        self._build_url_mapping()
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            # Scan the JSON directory for seed files
            self._scan_json_directory()
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                self._scan_json_directory()  

    def _build_url_mapping(self):
        """Build a mapping from URLs to file paths by reading all JSON files"""
        json_dir = Path(self.config.json_dir)
        
        if not json_dir.exists():
            self.logger.error(f"JSON directory {json_dir} does not exist!")
            return
        
        self.logger.info(f"Building URL to file mapping from {json_dir}...")
        
        # Find all JSON files recursively
        json_files = list(json_dir.rglob('*.json'))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    url = data.get('url')
                    if url:
                        # Normalize the URL before storing
                        from scraper import normalize_url
                        normalized_url = normalize_url(url)
                        # Remove fragment
                        from urllib.parse import urldefrag
                        normalized_url, _ = urldefrag(normalized_url)
                        
                        self.url_to_file_map[normalized_url] = str(json_file)
            except Exception as e:
                self.logger.error(f"Error reading {json_file}: {e}")
                continue
        
        self.logger.info(f"Built mapping for {len(self.url_to_file_map)} URLs")

    def _scan_json_directory(self):
        """Scan the JSON directory and add all JSON files as seeds"""
        json_dir = Path(self.config.json_dir)
        
        if not json_dir.exists():
            self.logger.error(f"JSON directory {json_dir} does not exist!")
            return
        
        # Find all JSON files recursively
        json_files = list(json_dir.rglob('*.json'))
        self.logger.info(f"Found {len(json_files)} JSON files in {json_dir}")
        
        for json_file in json_files:
            self.add_url(str(json_file))

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            # queue is already thread-safe, no need to lock
            return self.to_be_downloaded.get_nowait()
        except Empty:
            return None

    def add_url(self, filepath):
        filepath = normalize(filepath)
        urlhash = get_urlhash(filepath)
        add = False
        with self.lock: # for self.save changes
            if urlhash not in self.save:
                self.save[urlhash] = (filepath, False)
                self.save.sync()
                add = True
        # Queue is thread safe, so we can use add variable to move it outside lock
        if add:
            self.to_be_downloaded.put(filepath)
    
    def mark_url_complete(self, filepath):
        urlhash = get_urlhash(filepath)
        with self.lock: # for self.save changes
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {filepath}, but have not seen it before.")

            self.save[urlhash] = (filepath, True)
            self.save.sync()

    def get_url_to_file_map(self):
        """Return the URL to file mapping"""
        return self.url_to_file_map

from threading import Thread
from pathlib import Path
from utils import get_logger
import scraper
import time



class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        url_to_file_map = self.frontier.get_url_to_file_map()

        # Process files in batches for better performance
        processed = 0

        while True:
            tbd_file = self.frontier.get_tbd_url()
            if not tbd_file:
                self.logger.info(f"Frontier is empty. Processed {processed} files.")
                break

            # Process the JSON file
            try:
                self.logger.info(f"Processing {tbd_file}")
                scraped_files = scraper.scraper(
                    tbd_file, 
                    self.config.json_dir,
                    url_to_file_map
                )
                
                for scraped_file in scraped_files:
                    self.frontier.add_url(scraped_file)
                    
                self.frontier.mark_url_complete(tbd_file)
                processed += 1

                # Log progress every 1000 files instead of every file
                if processed % 1000 == 0:
                    self.logger.info(f"Processed {processed} files")
                
            except Exception as e:
                self.logger.error(f"Error processing {tbd_file}: {e}")
                self.frontier.mark_url_complete(tbd_file)
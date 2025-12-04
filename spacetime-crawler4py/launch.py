
import json
import time
import multiprocessing
from pathlib import Path
from configparser import ConfigParser
from argparse import ArgumentParser

from utils.config import Config
from crawler import Crawler

from index_vars import URL_id_index, page_rank
from analyze import write_analysis_to_file, indexer
from query import process_query


def main(config_file, restart, json_dir=None):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)

    # Override JSON directory if provided via command line
    if json_dir:
        config.set_json_dir(json_dir)

    # Verify the JSON directory exists
    if not Path(config.json_dir).exists():
        print(f"Error: JSON directory '{config.json_dir}' does not exist!")
        return

    crawler = Crawler(config, restart)
    crawler.start()
    
    # makes sure to save the rest of the documents
    indexer.save_batch_to_disk()
    # finally merge all the buckets into one index
    indexer.merge_all_buckets(cleanup_temp=True)

    # json_index.write_to_file(file="inverted_index.json")
    URL_id_index.write_to_file(file="url_id_index.json")
    page_rank.compute_rank()
    write_analysis_to_file()


if __name__ == "__main__":
    # multiprocessing.set_start_method('fork', force=True)
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    parser.add_argument("--json_dir", type=str, required=True, 
                       help="Path to directory containing JSON files")
    args = parser.parse_args()
    # main(args.config_file, args.restart, args.json_dir)
    str_input = ""
    while (str_input != "exit"):
        str_input = process_query.user_input()
        if (str_input == "exit"):
            break
        start_time = time.time()
        top_urls = process_query.query(str_input)
        process_query.print_query_results(top_urls)
        end_time = time.time()
        time_elapsed = end_time - start_time
        print(f"Total query time for '{str_input}': {time_elapsed:.4f} seconds")


import json
import time
import multiprocessing
from pathlib import Path
from configparser import ConfigParser
from argparse import ArgumentParser

from utils.config import Config
from crawler import Crawler
from index_vars import json_index, URL_id_index
from analyze import write_analysis_to_file
from query import query, user_input, extract_terms




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

    # write our analysis when our crawler ends
    json_index.write_to_file(file="inverted_index.json")
    URL_id_index.write_to_file(file="url_id_index.json")
    write_analysis_to_file()

    # get user input and query
    user_in = user_input()
    # keep track of query time after user clicks enter
    start_time = time.time()
    tokens = extract_terms(user_in)
    urls = query(tokens)
    ### print/display the urls here ###
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f"Total query time for '{user_in}': {time_elapsed:.2f} seconds")


if __name__ == "__main__":
    multiprocessing.set_start_method('fork', force=True)
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    parser.add_argument("--json_dir", type=str, required=True, 
                       help="Path to directory containing JSON files")
    args = parser.parse_args()
    main(args.config_file, args.restart, args.json_dir)
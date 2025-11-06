
import json
import multiprocessing
from pathlib import Path
from configparser import ConfigParser
from argparse import ArgumentParser

from utils.config import Config
from crawler import Crawler

from analyze import write_analysis_to_file


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
    write_analysis_to_file()


if __name__ == "__main__":
    multiprocessing.set_start_method('fork', force=True)
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    parser.add_argument("--json_dir", type=str, required=True, 
                       help="Path to directory containing JSON files")
    args = parser.parse_args()
    main(args.config_file, args.restart, args.json_dir)
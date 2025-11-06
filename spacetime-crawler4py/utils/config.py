

class Config(object):
    def __init__(self, config):
        # User agent (optional for local files, but keeping for compatibility)
        self.user_agent = config.get("IDENTIFICATION", "USERAGENT", fallback="Local JSON Crawler")
        
        # Thread count
        self.threads_count = config.getint("LOCAL PROPERTIES", "THREADCOUNT", fallback=16)
        
        # Save file for progress
        self.save_file = config.get("LOCAL PROPERTIES", "SAVE", fallback="frontier.shelve")
        
        # Get JSON directory from config or will be set via command line
        self.json_dir = config.get("CRAWLER", "JSON_DIR", fallback="./json_files")
        
        # Time delay between processing files
        self.time_delay = config.getfloat("CRAWLER", "POLITENESS", fallback=0.01)

    def set_json_dir(self, json_dir):
        """Set JSON directory from command line argument"""
        self.json_dir = json_dir
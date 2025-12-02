from index import URLIndex
from threading import Lock
from page_rank import PageRanker

json_index_lock = Lock()
URL_id_index = URLIndex()
url_index_lock = Lock()

page_rank = PageRanker()
from index import URLIndex
from threading import Lock

json_index_lock = Lock()
URL_id_index = URLIndex()
url_index_lock = Lock()
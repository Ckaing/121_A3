from index import URLIndex, Index
from threading import Lock

json_index = Index()
json_index_lock = Lock()
URL_id_index = URLIndex()
url_index_lock = Lock()
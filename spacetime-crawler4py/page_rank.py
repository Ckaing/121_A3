import orjson
from threading import Lock
from collections import defaultdict

class PageRanker:
    def __init__(self, filename='pagerank.json'):
        self.page_outlinks = defaultdict(set)
        self.page_rank_lock = Lock()
        self.save_path = filename

    def update_links(self, url, outgoing_urls):
        with self.page_rank_lock:
            self.page_outlinks[url].update(outgoing_urls)

    # on slide27 lec24, it says in practice ~5 iterations is sufficient
    def _calculate_page_rank(self, damping=0.85, iter=5):
        pages = list(page_outlinks.keys())
        n = len(pages)

        if n == 0:
            return {}

        # Initialize pagerank=1 for each page
        pr = {id: 1.0 for id in pages}

        #TODO: idk if this is the smartest thing to do cause rn my inlink and outlink are all the urls themselves
        # not the id since not all inlink/outlinks are guaranteed to be an "aprpoved" link that we will crawl, but it still counts
        # i think? also analysis is the only time the id is referenced/updated so i don't really know how to add it in 
        # during the scraper.py phase where we get all the links... 

        for i in range(iter):
            new_pr = {}
            # iterate over each page
            for p in pages:
                rank_sum = 0
                # sum contributions from in-links (sum j=1...N: (Lij/cj)*pj)
                for src, outlinks in self.page_outgoing_links.items():
                    if p in outlinks: # Lij
                        outdeg = len(outlinks)  # C(Ti)
                        if outdeg > 0:
                            # PR(Ti) / C(Ti)
                            rank_sum += pr[src] / outdeg
                # pi = (1-d) + d(sum from j=1...N: (Lij/cj)*pj)
                new_pr[p] = (1 - damping) + damping * rank_sum

            # update
            pr = new_pr

        return pr


    def _save_page_rank(self, pagerank):
        with open(self.save_path, "wb", encoding="utf-8") as f:
            orjson.dump(pagerank, f)
    

    def compute_rank(self, URL_id_index_path):
        with open(URL_id_index_path, 'rb') as f:
            URL_id_index = orjson.loads(f.read())
        pr = self._calculate_page_rank(URL_id_index)
        self._save_page_rank(pr)
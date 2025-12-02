from collections import deque
from threading import RLock

from tokenizer import tokenize


class ThreeGram(object):
    def __init__(self, capacity=50, threshold=0.9):
        self.SIMILARITY_THRESHOLD = threshold
        self.prev_pages = deque(maxlen=capacity)
        self.lock = RLock()

    def similar(self, content):
        tokens = tokenize(content)
        if tokens is None:
            return False
        gram = self.get_3gram(tokens)
        with self.lock: # for controlling access to prev_pages
            for prev in self.prev_pages:
                score = self.similarity_score(prev, gram)
                if score >= self.SIMILARITY_THRESHOLD:
                    return True
            self.prev_pages.append(gram)
        return False

    def get_3gram(self, tokens):
        grams = set()
        for i in range(len(tokens) - 2):
            # add hash to tuple to take up less memory
            grams.add(hash((tokens[i], tokens[i + 1], tokens[i + 2])))
        return grams

    def similarity_score(self, gram_1, gram_2):
        intersection = len(gram_1 & gram_2)
        # union = |A| + |B| + |A and B| --> that way we don't waste time computing A | B
        union = len(gram_1) + len(gram_2) + intersection
        if union == 0:
            return 0
        similarity_score = intersection / union 
        return similarity_score
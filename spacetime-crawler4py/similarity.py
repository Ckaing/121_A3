from collections import deque
from threading import RLock

from tokenizer import tokenize


class ThreeGram(object):
    def __init__(self, capacity=50, threshold=0.95):
        self.SIMILARITY_THRESHOLD = threshold
        self.prev_pages = deque(maxlen=capacity)
        self.tmp_prev_filepath = deque(maxlen=capacity) # NOTE DELETE THIS, THIS IS JUST FOR TESTING
        self.lock = RLock()

    def similar(self, content, filepath=''):
        tokens = tokenize(content)
        if tokens is None:
            return False
        gram = self.get_3gram(tokens)
        with self.lock: # for controlling access to prev_pages
            for i in range(len(self.prev_pages)): # NOTE change back to 'for prev in self.prev_pages'
                score = self.similarity_score(self.prev_pages[i], gram) # NOTE change back to 'score = self.similarity_score(prev, gram)'
                if score >= self.SIMILARITY_THRESHOLD:
                    self.log_similar(filepath, self.tmp_prev_filepath[i], score) # NOTE DELETE LATER
                    return True
            self.prev_pages.append(gram)
            self.tmp_prev_filepath.append(filepath) # NOTE DELTE LATER
        return False

    def get_3gram(self, tokens):
        grams = set()
        for i in range(len(tokens) - 2):
            # add hash to tuple to take up less memory
            grams.add(hash((tokens[i], tokens[i + 1], tokens[i + 2])))
        return grams

    def similarity_score(self, gram_1, gram_2):
        intersection = len(gram_1 & gram_2)
        # union = |A| + |B| - |A and B| --> that way we don't waste time computing A | B
        union = len(gram_1) + len(gram_2) - intersection
        if union == 0:
            return 0
        similarity_score = intersection / union 
        return similarity_score

    # NOTE DELETE LATER
    def log_similar(self, fp1, fp2, score, folder='tmp_similar_log/'):
        try:
            with open(folder + 'file_paths.txt', 'a') as f:
                f.write('SCORE: ' + str(score) + '\n')
                f.write('PATH1: ' + fp1 + '\n')
                f.write('PATH2: ' + fp2 + '\n')
                f.write('\n\n\n')

        except Exception as e:
            print('Error writing log, just didn\'t want to crash program')
            print('Error:', str(e))


similarity_checker = ThreeGram()
# run the following to enable nltk
# pip install nltk
from nltk.stem import SnowballStemmer


class Stemmer:
    def __init__(self) -> None:
        self.stemmer = SnowballStemmer("english")
        self.cache = {}  # improve performance for already stemmed words
        self.exceptions = self._load_exceptions()

    def _load_exceptions(self):
        """Keeps dictionary of words we do not want to be stemmed."""
        return {
            # add words that we want to keep the same, NOT stemmed
            # i.e. news -> news, universal -> universal (not univers), etc.
            "repository": "repository",
            "machine": "machine",
            "database": "database",
            "series": "series",
            "instances": "instance",
            "attribute": "attribute",
            "categorical": "category",
            "integer": "integer",
            "missing": "missing",
            "university": "university"
        }

    def stem(self, token):
        if (token in self.cache):
            return self.cache[token]

        if token.lower() in self.exceptions:
            results = self.exceptions[token.lower()]
            self.cache[token] = results
            return results

        stemmed_word = self.stemmer.stem(token)
        self.cache[token] = stemmed_word
        return stemmed_word

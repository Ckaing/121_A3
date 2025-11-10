# Analytics:
#   number of indexed documents (len of URLIndex obj)
#   number of unique tokens (len of index)
    # if we store indexed files on disk, we can keep them in a folder and then iterate them to find and count unique tokens
#   total size in KB of index on disk (add on manually later)

class Analysis:
    def __init__(self, docs, tokens) -> None:
        self.docs = docs
        self.tokens = tokens

    def __str__(self) -> str:
        analysis_string = "Number of Indexed Documents: "
        analysis_string += self.docs
        analysis_string += "\nNumber of Unique Tokens: "
        analysis_string += self.tokens
        analysis_string += "\n Total Size on Disk (in KB): \n"
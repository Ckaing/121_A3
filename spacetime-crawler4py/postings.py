class Posting:
    def __init__(self):
        self.posting = {}
        self.fields = {}
        self.position = {}

    def add_entry(self, docID, freq, fields: str, positions: int):
        self.posting[docID] = freq
        self.fields[docID] = fields
        self.position[docID] = positions
    
 # write the encoding for writing to json files
 # return the object as an explicit dict

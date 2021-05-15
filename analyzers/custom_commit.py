class CustomCommit:
    def __init__(self, index=None, pydrillerCommitObj=None):
        if pydrillerCommitObj == None:
            self.commit = {}
        else: 
            self.commit.setCommit(index, pydrillerCommitObj)

    def setCommit(self, index, pydrillerCommitObj):
        self.commit = {
            "commit_index": index,
            "author": pydrillerCommitObj.author.name,
            "date": pydrillerCommitObj.author_date,
            "commit_hash": pydrillerCommitObj.hash,
            "commit_message": pydrillerCommitObj.msg
        }
    
    @classmethod
    def get_total_count_authors(cls, customCommitList):
        authors = set()
        for el in customCommitList:
            authors.add(el["author"])
        
        return len(authors)
    
    @classmethod
    def get_authors_count_between(cls, customCommitList, initialIndex, finalIndex):
        sortedList = sorted(customCommitList, key=lambda x: x["commit_index"])
        authors = set()

        for i in range(initialIndex, finalIndex):
            authors.add(sortedList[i]["author"])

        return len(authors)
    
    @classmethod
    def indexOf(cls, customCommitList, commit_hash):
        for commit in customCommitList:
            if commit["commit_hash"] == commit_hash:
                return commit["commit_index"]
        
        raise IndexError

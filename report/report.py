import statistics
from pprint import PrettyPrinter

def mean(values):
    return round(statistics.mean(values), 2) if len(values) > 0 else '-'

def median(values):
    return round(statistics.median(values),2) if len(values) > 0 else '-'

def safe_max(values):
    return max(values) if len(values) > 0 else '-'

def safe_min(values):
    return min(values) if len(values) > 0 else '-'

class Report:
    def __init__(self):
        self.metrics_per_category = {
            'unittest': [],
            'pytest': [],
            'ongoing': [],
            'migrated': [],
            'unknown': []
        }
        self.aggregated_metrics = {
            'unittest': [],
            'pytest': [],
            'ongoing': [],
            'migrated': [],
            'unknown': []
        }
        return

    """
    For each category we will have a metrics object with the following keys:
    data: 
        CATEGORY
        REPOSITORY_NAME: name of the repository
        REPOSITORY_LINK: github link to the repository
        
        NOC: number of commits analyzed. All commits in the repository.
        NOC_UNITTEST: number of commits using unittest
        NOC_PYTEST: number of commits using pytest
        NOC_BOTH: number of commits using unittest

        OCM: the migration happened in one commit?
        NOD: number of days the migration took (or is taking)

        NOF = Number of files analyzed
        NOF_UNITTEST: Number of files using unittest
        NOF_PYTEST: Number of files using pytest
        NOF_BOTH: Number of files using both frameworks

        FC_UNITTEST: First commit hash where a reference to unittest was added
        FC_PYTEST: First commit hash where a reference to pytest was added
        FC_UNITTEST_LINK: First commit link where a reference to unittest was added
        FC_PYTEST_LINK: First commit link where a reference to pytest was added

        'LC_UNITTEST': self.unittest_occurrences.last['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
        'LC_PYTEST': self.pytest_occurrences.last['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
        'LC_UNITTEST_LINK': commit_base_url + self.unittest_occurrences.last['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
        'LC_PYTEST_LINK': com
    """
    def add(self, data):
        self.metrics_per_category[data['CATEGORY']].append(data)
        return

    def print(self, full=False):
        depth = 1 if not full else None
        pprinter = PrettyPrinter(depth=depth)

        print("Per category")
        for key, values in self.metrics_per_category.items():
            print("Category: {}".format(key))

            for repo in values:
                pprinter.pprint(repo)
            
        return

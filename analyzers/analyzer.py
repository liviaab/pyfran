
from io_utils.output import OutputUtil
from datetime import datetime

from analyzers.checkouts_analyzer import CheckoutsAnalyzer
from analyzers.delta_commits_analyzer import DeltaCommits

from classifiers.main_classifier import MainClassifier

from report.column_names import *

class Analyzer:
    def __init__(self, repo_url, out_dir):
        self.out_dir = out_dir
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]

    def process_and_classify(self):
        print("Time marker #2 - process commits objects", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # Step 1: Using Pydriller, get commit information and select
        # commits of interest
        # self.__process_commits()
        dc_analyzer = DeltaCommits(self.repo_url)
        (allcommits, unittest_occurrences, pytest_occurrences) = dc_analyzer.process_delta_commits()

        print("Time marker #3 - process files from each checkout", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # Step 2: Clone the repo and visit each checkout to get information
        # about tests through time
        apis_info = CheckoutsAnalyzer(self.repo_url).process_checkouts(allcommits)

        # Step 3: Even with the past information, we still need to check out
        # the current repo state to determine whether if it is "migrated" or "ongoing"
        print("Time marker #4 - classify", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # data = self.__classify_and_process_metrics()
        classifier = MainClassifier(self.repo_url, allcommits, unittest_occurrences, pytest_occurrences)
        (data, author_infos) = classifier.classify_and_process_metrics()

        # Output the retrieved information in CSVs
        print("Time marker #5 - create csv with commits, authors and APIs information", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        columns = commit_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_commit", allcommits, columns, self.out_dir)

        columns = api_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_api", apis_info, columns, self.out_dir)

        columns = author_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_authors", author_infos, columns, self.out_dir)

        return data

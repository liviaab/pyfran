
from io_utils.output import OutputUtil
from datetime import datetime

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
        (allcommits, unittest_occurrences, pytest_occurrences, migration_occurrences) = dc_analyzer.process_delta_commits()

        # Step 3: Even with the past information, we still need to check out
        # the current repo state to determine whether if it is "migrated" or "ongoing"
        print("Time marker #3 - classify", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # data = self.__classify_and_process_metrics()
        classifier = MainClassifier(self.repo_url, allcommits, unittest_occurrences, pytest_occurrences, migration_occurrences)
        (data, author_infos) = classifier.classify_and_process_metrics()

        # Output the retrieved information in CSVs
        print("Time marker #4 - create csv with commits and authors information", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        columns = commit_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_commit", allcommits, columns, self.out_dir)

        columns = author_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_authors", author_infos, columns, self.out_dir)

        return data

from io_utils.output import OutputUtil
import os
from datetime import datetime

from pydriller import RepositoryMining
from pyparsing import pythonStyleComment

from heuristics.file import FileHeuristics as fh
from heuristics.pytest import PytestHeuristics as ph
from heuristics.unittest import UnittestHeuristics as uh

from analyzers.custom_commit import CustomCommit
from analyzers.occurrences import Occurrences
from analyzers.repository_analyzer import RepositoryAnalyzer

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

class CommitsAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]
        self.noc_unittest = 0
        self.noc_pytest = 0
        self.noc_both = 0
        self.unittest_occurrences = Occurrences()
        self.pytest_occurrences = Occurrences()
        self.memo = {
            "unittest_in_code": False,
            "unittest_in_removed_diffs": False,
            "pytest_in_code": False,
            "pytest_in_removed_diffs": False,
            "is_test_file": False
        }
        self.commits = []

    def process_and_classify(self):
        print("Time marker #2 - process commits", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.__process_commits()

        print("Time marker #3 - classify", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        data = self.__classify_and_process_metrics()

        print("Time marker #3.5 - dump commit messages", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        columns = ["commit_index", "author", "date", "commit_hash", "commit_message"]
        OutputUtil.create_out_path("commit_messages/")
        OutputUtil.output_list_as_csv(self.project_name, self.commits, columns, "commit_messages/")

        return data

    def __process_commits(self):
        print("Analyzing {}...".format(self.project_name))
        try:
            self.__do_process_commits("master")
        except:
            self.__do_process_commits("main")

        print("Analyzed {} commits.".format(len(self.commits)))
        return

    def __do_process_commits(self, branch):
        miner = RepositoryMining(self.repo_url, only_no_merge=True)
        index = 0
        for commit in miner.traverse_commits():
            now = datetime.now()
            print("\t\t{} at {}".format(commit.hash, now.strftime("%d/%m/%Y %H:%M:%S")))

            custom = CustomCommit(index, commit)
            self.commits.append(custom.commit)

            for modification in commit.modifications:
                _filename, extension = os.path.splitext(modification.filename)
                if modification.source_code == None or extension not in VALID_EXTENSIONS:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(index, commit, modification)

            index += 1

        return

    def __classify_and_process_metrics(self):
        """
            classes: unittest | pytest | ongoing | migrated | unknown
        """
        currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
        currentDefaultBranch.search_frameworks()

        commit_base_url = self.repo_url + '/commit/'

        amount_total_commits = len(self.commits)
        number_of_authors = CustomCommit.get_total_count_authors(self.commits)

        base = {
            'REPOSITORY_NAME': self.project_name,
            'REPOSITORY_LINK': self.repo_url,
            
            'NOC': amount_total_commits,

            'NOD': 0,
            'OCM': False,
            'NOA': number_of_authors,
            'NOMA': '-',

            'NOF': currentDefaultBranch.count_files(),
            'NOF_UNITTEST': currentDefaultBranch.nof_unittest,
            'NOF_PYTEST': currentDefaultBranch.nof_pytest,
            'NOF_BOTH': currentDefaultBranch.nof_both,

            'FC_UNITTEST': self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST': self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,
            'FC_UNITTEST_LINK': commit_base_url + self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST_LINK': commit_base_url + self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,

            'LC_UNITTEST': self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST': self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
            'LC_UNITTEST_LINK': commit_base_url + self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST_LINK': commit_base_url + self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
        }

        if not self.unittest_occurrences.has_first_occurrence() \
            and self.pytest_occurrences.has_first_occurrence():

            data = {
                'CATEGORY': 'pytest',
                'NOC_UNITTEST': 0,
                'NOC_PYTEST': amount_total_commits,
                'NOC_BOTH': 0
            }
            base.update(data)
            return base

        if not self.pytest_occurrences.has_first_occurrence() \
            and self.unittest_occurrences.has_first_occurrence():
            data = {
                'CATEGORY': 'unittest',
                'NOC_UNITTEST': amount_total_commits,
                'NOC_PYTEST': 0,
                'NOC_BOTH': 0
            }
            base.update(data)
            return base

        if (self.unittest_occurrences.has_first_occurrence() \
            and self.pytest_occurrences.has_first_occurrence()):
            idx_first_unittest_commit = CustomCommit.indexOf(self.commits, self.unittest_occurrences.first.commit["commit_hash"])
            idx_first_pytest_commit = CustomCommit.indexOf(self.commits, self.pytest_occurrences.first.commit["commit_hash"])
            timedelta = self.unittest_occurrences.last.commit["date"] - self.pytest_occurrences.first.commit["date"] 

            if(currentDefaultBranch.usesPytest and not currentDefaultBranch.usesUnittest):
                idx_last_unittest_commit = CustomCommit.indexOf(self.commits, self.unittest_occurrences.last.commit["commit_hash"])
                number_of_migration_authors = CustomCommit.get_authors_count_between(self.commits, idx_first_pytest_commit, idx_last_unittest_commit)

                data = {
                    'CATEGORY': 'migrated',
                    'NOC_UNITTEST': idx_last_unittest_commit - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': idx_last_unittest_commit - idx_first_pytest_commit,
                    'OCM': True if idx_last_unittest_commit == idx_first_pytest_commit else False,
                    'NOD': timedelta.days,
                    'NOMA': number_of_migration_authors
                }
                base.update(data)
                return base

            if(currentDefaultBranch.usesPytest and currentDefaultBranch.usesUnittest):
                number_of_migration_authors = CustomCommit.get_authors_count_between(self.commits, idx_first_pytest_commit, amount_total_commits - 1)

                data = {
                    'CATEGORY': 'ongoing',
                    'NOC_UNITTEST': amount_total_commits - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': amount_total_commits - idx_first_pytest_commit,
                    'NOD': timedelta.days,
                    'NOMA': number_of_migration_authors
                }
                base.update(data)
                return base

        data = {'CATEGORY': 'unknown'}
        base.update(data)
        return base

    def __get_lines_from_diff(self, parsed_modifications):
        return [ removed_line for line, removed_line in parsed_modifications ]

    def __match_patterns(self, modification):
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])
        added_lines = self.__get_lines_from_diff(modification.diff_parsed['added'])

        self.memo = {
            "unittest_in_code": uh.matches_any(added_lines),
            "unittest_in_removed_diffs": uh.matches_any(removed_lines, ignoreComments=False),
            "pytest_in_code": ph.matches_any(added_lines),
            "pytest_in_removed_diffs": ph.matches_any(removed_lines, ignoreComments=False),
            "is_test_file": fh.matches_test_file(modification.new_path)
        }

        return

    def __update_occurrences(self, index, commit, modification):
        if self.__can_update_unittest_first_occurrence():
            self.unittest_occurrences.set_first_occurrence(index, commit)

        if self.__can_update_unittest_last_occurrence():
            self.unittest_occurrences.set_last_occurrence(index, commit)

        if self.__can_update_pytest_first_occurrence():
            self.pytest_occurrences.set_first_occurrence(index, commit)

        if self.__can_update_pytest_last_occurrence():
            self.pytest_occurrences.set_last_occurrence(index, commit)

        return

    def __can_update_unittest_first_occurrence(self):
        return (not self.unittest_occurrences.has_first_occurrence()) \
            and self.memo["unittest_in_code"]

    def __can_update_pytest_first_occurrence(self):
        return (not self.pytest_occurrences.has_first_occurrence()) \
            and self.memo["pytest_in_code"]

    def __can_update_unittest_last_occurrence(self):
        return self.unittest_occurrences.has_first_occurrence() \
                and (self.memo["unittest_in_removed_diffs"])

    def __can_update_pytest_last_occurrence(self):
        return self.pytest_occurrences.has_first_occurrence() \
            and self.memo["pytest_in_removed_diffs"]

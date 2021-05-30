import os
import shutil
from io_utils.output import OutputUtil
from datetime import datetime, timezone

from pydriller import RepositoryMining
from git import Repo
from pyparsing import pythonStyleComment

from heuristics.test_file import TestFileHeuristics as fh
from heuristics.pytest import PytestHeuristics as ph
from heuristics.unittest import UnittestHeuristics as uh
from heuristics.test_methods import TestMethodsHeuristics as mh
from heuristics.apis import UnittestAPIHeuristics as uAPIh, PytestAPIHeuristics as pAPIh

from analyzers.custom_commit import CustomCommit
from analyzers.occurrences import Occurrences
from analyzers.repository_analyzer import RepositoryAnalyzer

from report.column_names import *

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

class CommitsAnalyzer:
    def __init__(self, repo_url, out_dir):
        self.out_dir = out_dir
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
        self.author_infos = []
        self.apis_info = []

    def process_and_classify(self):
        print("Time marker #2 - process commits objects", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.__process_commits()

        print("Time marker #3 - process files from each checkout", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.__process_checkouts()

        print("Time marker #4 - classify", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        data = self.__classify_and_process_metrics()

        print("Time marker #5 - create csv with commits, authors and APIs information", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        columns = commit_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_commit", self.commits, columns, self.out_dir)

        columns = api_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_api", self.apis_info, columns, self.out_dir)

        columns = author_columns()
        OutputUtil.output_list_as_csv(self.project_name+"_authors", self.author_infos, columns, self.out_dir)

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
        index = 0
        for commit in RepositoryMining(self.repo_url, only_no_merge=True).traverse_commits():
            print("\t\tcommit {}".format(commit.hash))

            commit_memo = {
                "unittest_in_code": False,
                "unittest_in_removed_diffs": False,
                "pytest_in_code": False,
                "pytest_in_removed_diffs": False,
                "has_test_file": False
            }

            for modification in commit.modifications:
                _filename, extension = os.path.splitext(modification.filename)
                if modification.source_code == None or extension not in VALID_EXTENSIONS:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(index, commit, modification)

                commit_memo = {
                    "unittest_in_code": commit_memo["unittest_in_code"] or self.memo["unittest_in_code"],
                    "unittest_in_removed_diffs": commit_memo["unittest_in_removed_diffs"] or self.memo["unittest_in_removed_diffs"],
                    "pytest_in_code": commit_memo["pytest_in_code"] or self.memo["pytest_in_code"],
                    "pytest_in_removed_diffs": commit_memo["pytest_in_removed_diffs"] or self.memo["pytest_in_removed_diffs"],
                    "has_test_file": commit_memo["has_test_file"] or self.memo["is_test_file"]
                }

            custom = CustomCommit(index, commit, commit_memo)
            self.commits.append(custom.commit)
            index += 1

        return

    def __process_checkouts(self):
        local_path_to_repo = self.repo_url.split('/')[-1]
        repo = Repo.clone_from(self.repo_url, local_path_to_repo)

        # import code; code.interact(local=dict(globals(), **locals()))

        for commit in self.commits:
            repo.git.checkout(commit["commit_hash"])
            print("\t\tChecking out commit", commit["commit_hash"])

            test_files = 0
            test_methods = 0

            testCaseSubclasses = 0
            u_api_asserts = 0
            u_api_setUps = 0
            u_api_setUpClasses = 0
            u_api_tearDown = 0
            u_api_tearDownClasses = 0
            u_api_skiptests = 0
            u_api_expectedFailures = 0

            p_api_asserts = 0
            p_api_raiseError = 0
            p_api_skiptests = 0
            p_api_expectedFailures = 0
            p_api_fixtures = 0

            for path, _, files in os.walk(local_path_to_repo):
                if '.git' in path:
                    continue

                for filepath in files:
                    _name, extension = os.path.splitext(filepath)

                    if extension not in VALID_EXTENSIONS:
                        continue

                    is_test_file = fh.matches_test_file(filepath)

                    if is_test_file:
                        test_files += 1

                        with open(os.path.join(path, filepath), 'r') as src:
                            content = src.read()
                            test_methods += mh.count_test_methods(content)

                            quantity_by_api = uAPIh.count_apis(content)

                            testCaseSubclasses += quantity_by_api["testCaseSubclass"]
                            u_api_asserts += quantity_by_api["assert"]
                            u_api_setUps += quantity_by_api["setUp"]
                            u_api_setUpClasses += quantity_by_api["setUpClass"]
                            u_api_tearDown += quantity_by_api["tearDown"]
                            u_api_tearDownClasses += quantity_by_api["tearDownClass"]
                            u_api_skiptests += quantity_by_api["skipTest"]
                            u_api_expectedFailures += quantity_by_api["expectedFailure"]

                            quantity_by_api = pAPIh.count_apis(content)
                            p_api_asserts += quantity_by_api["assert"]
                            p_api_raiseError += quantity_by_api["raiseError"]
                            p_api_skiptests += quantity_by_api["skipTest"]
                            p_api_expectedFailures += quantity_by_api["expectedFailure"]
                            p_api_fixtures += quantity_by_api["fixture"]

            apis_in_commit = {
                "commit_index": commit["commit_index"],
                "author_email": commit["author_email"],
                "date": commit["date"],
                "commit_hash": commit["commit_hash"],

                "test_files": test_files,
                "test_methods": test_methods,

                "u_api_testCaseSubclass": testCaseSubclasses,
                "u_api_assert": u_api_asserts,
                "u_api_setUp": u_api_setUps,
                "u_api_setUpClass": u_api_setUpClasses,
                "u_api_tearDown": u_api_tearDown,
                "u_api_tearDownClass": u_api_tearDownClasses,
                "u_api_skiptest": u_api_skiptests,
                "u_api_expectedFailure": u_api_expectedFailures,

                "p_api_assert": p_api_asserts,
                "p_api_raiseError": p_api_raiseError,
                "p_api_skiptest": p_api_skiptests,
                "p_api_expectedFailure": p_api_expectedFailures,
                "p_api_fixture": p_api_fixtures
            }

            self.apis_info.append(apis_in_commit)

        if os.path.exists(local_path_to_repo) and os.path.isdir(local_path_to_repo):
            shutil.rmtree(local_path_to_repo)

        return

    def __classify_and_process_metrics(self):
        """
            classes: unittest | pytest | ongoing | migrated | unknown
        """

        currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
        currentDefaultBranch.search_frameworks()

        commit_base_url = self.repo_url + '/commit/'

        amount_total_commits = len(self.commits)
        number_of_authors_names, number_of_authors_emails  = CustomCommit.get_total_count_authors(self.commits)

        base = {
            'REPOSITORY_NAME': self.project_name,
            'REPOSITORY_LINK': self.repo_url,
            
            'NOC': amount_total_commits,

            'NOD': 0,
            'OCM': False,
            'NOA (name)': number_of_authors_names,
            'NOMA (name)': 0,
            "NOMAP (name)": 0,
            'NOA (email)': number_of_authors_emails,
            'NOMA (email)': 0,
            "NOMAP (email)": 0,
            "NOA email - name": number_of_authors_emails - number_of_authors_names,
            "PBU": False,

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
            self.author_infos = CustomCommit.characterize_authors(self.commits, amount_total_commits + 1, amount_total_commits + 1)
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
            self.author_infos = CustomCommit.characterize_authors(self.commits, amount_total_commits + 1, amount_total_commits + 1)

            data = {
                'CATEGORY': 'unittest',
                'NOC_UNITTEST': amount_total_commits,
                'NOC_PYTEST': 0,
                'NOC_BOTH': 0
            }
            base.update(data)
            return base

        if not self.pytest_occurrences.has_first_occurrence() \
            and not self.unittest_occurrences.has_first_occurrence():

            data = {
                'CATEGORY': 'unknown',
                'NOC_UNITTEST': 0,
                'NOC_PYTEST': 0,
                'NOC_BOTH': 0,
            }
            base.update(data)
            return base

        idx_first_unittest_commit = CustomCommit.indexOf(self.commits, self.unittest_occurrences.first.commit["commit_hash"])
        idx_first_pytest_commit = CustomCommit.indexOf(self.commits, self.pytest_occurrences.first.commit["commit_hash"])

        if (self.unittest_occurrences.has_first_occurrence() and \
            self.pytest_occurrences.has_first_occurrence()) and \
            idx_first_unittest_commit <= idx_first_pytest_commit:

            if(currentDefaultBranch.usesPytest and not currentDefaultBranch.usesUnittest):
                idx_last_unittest_commit = CustomCommit.indexOf(self.commits, self.unittest_occurrences.last.commit["commit_hash"])
                number_of_migration_authors_names, number_of_migration_authors_emails = \
                    CustomCommit.get_authors_count_between(self.commits, idx_first_pytest_commit, idx_last_unittest_commit)
                timedelta = self.unittest_occurrences.last.commit["date"] - self.pytest_occurrences.first.commit["date"]

                self.author_infos = CustomCommit.characterize_authors(self.commits, idx_first_pytest_commit, idx_last_unittest_commit)
                data = {
                    'CATEGORY': 'migrated',
                    'NOC_UNITTEST': idx_last_unittest_commit - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': idx_last_unittest_commit - idx_first_pytest_commit,
                    'OCM': True if idx_last_unittest_commit == idx_first_pytest_commit else False,
                    'NOD': timedelta.days,
                    'NOMA (name)': number_of_migration_authors_names,
                    "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"]* 100, 2),
                    'NOMA (email)': number_of_migration_authors_emails,
                    "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"]* 100, 2)
                }
                base.update(data)
                return base

            if(currentDefaultBranch.usesPytest and currentDefaultBranch.usesUnittest):
                number_of_migration_authors_names, number_of_migration_authors_emails = \
                    CustomCommit.get_authors_count_between(self.commits, idx_first_pytest_commit, amount_total_commits - 1)

                timedelta = datetime.now(timezone.utc) - self.pytest_occurrences.first.commit["date"]

                self.author_infos = CustomCommit.characterize_authors(self.commits, idx_first_pytest_commit, amount_total_commits -1)
                data = {
                    'CATEGORY': 'ongoing',
                    'NOC_UNITTEST': amount_total_commits - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': amount_total_commits - idx_first_pytest_commit,
                    'NOD': timedelta.days,
                    'NOMA (name)': number_of_migration_authors_names,
                    "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"] * 100, 2),
                    'NOMA (email)': number_of_migration_authors_emails,
                    "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"]* 100, 2)
                }
                base.update(data)
                return base

        pbu = idx_first_unittest_commit > idx_first_pytest_commit
        data = {
            'CATEGORY': 'unknown',
            'PBU': pbu,
            'NOC_UNITTEST': amount_total_commits - idx_first_unittest_commit,
            'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
            'NOC_BOTH': amount_total_commits - idx_first_unittest_commit if pbu else 0,
        }
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

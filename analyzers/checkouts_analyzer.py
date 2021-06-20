import os
import shutil
from git import Repo
from pyparsing import pythonStyleComment, cppStyleComment, quotedString

from common.common import VALID_EXTENSIONS, docString

from heuristics.test_file import TestFileHeuristics as fh
from heuristics.test_methods import TestMethodsHeuristics as mh
from heuristics.apis import UnittestAPIHeuristics as uAPIh, PytestAPIHeuristics as pAPIh

class CheckoutsAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.local_path_to_repo = repo_url.split('/')[-1]

    def process_checkouts(self, commits):
        repo = Repo.clone_from(self.repo_url, self.local_path_to_repo)

        apis_info = []

        for commit in commits:
            # if not commit["are_we_interested"]:
            #     continue
            if commit["commit_index"] % 5 != 0:
                continue

            repo.git.checkout(commit["commit_hash"])
            print("\t\tChecking out commit", commit["commit_hash"])

            test_files = 0
            test_methods = 0

            u_api_testCaseSubclasses = 0
            u_api_asserts = 0
            u_api_setUps = 0
            u_api_setUpClasses = 0
            u_api_tearDown = 0
            u_api_tearDownClasses = 0
            u_api_unittestSkiptests = 0
            u_api_selfSkiptests = 0
            u_api_expectedFailures = 0

            native_asserts = 0
            p_api_pytestRaises = 0
            p_api_simpleSkips = 0
            p_api_markSkips = 0
            p_api_expectedFailures = 0
            p_api_fixtures = 0
            p_api_useFixtures = 0
            p_api_genericMark = 0
            p_api_genericPytest = 0

            for path, _, files in os.walk(self.local_path_to_repo):
                if '.git' in path:
                    continue

                for filename in files:
                    _name, extension = os.path.splitext(filename)

                    if extension not in VALID_EXTENSIONS:
                        continue

                    is_test_file = fh.matches_test_file(os.path.join(path, filename))

                    if is_test_file:
                        test_files += 1

                        with open(os.path.join(path, filename), 'r') as src:
                            content = src.read()

                            content = (cppStyleComment|pythonStyleComment|quotedString|docString).suppress().transformString(content)

                            test_methods += mh.count_test_methods(content)
                            
                            quantity_by_api = uAPIh.check_apis(content)
                            u_api_testCaseSubclasses += quantity_by_api["count_testCaseSubclass"]
                            u_api_asserts += quantity_by_api["count_assert"]
                            u_api_setUps += quantity_by_api["count_setUp"]
                            u_api_setUpClasses += quantity_by_api["count_setUpClass"]
                            u_api_tearDown += quantity_by_api["count_tearDown"]
                            u_api_tearDownClasses += quantity_by_api["count_tearDownClass"]
                            u_api_unittestSkiptests += quantity_by_api["count_unittestSkipTest"]
                            u_api_selfSkiptests += quantity_by_api["count_selfSkipTest"]
                            u_api_expectedFailures += quantity_by_api["count_expectedFailure"]

                            quantity_by_api = pAPIh.check_apis(content)
                            native_asserts += quantity_by_api["count_native_assert"]
                            p_api_pytestRaises += quantity_by_api["count_pytestRaise"]
                            p_api_simpleSkips += quantity_by_api["count_simpleSkip"]
                            p_api_markSkips += quantity_by_api["count_markSkip"]
                            p_api_expectedFailures += quantity_by_api["count_expectedFailure"]
                            p_api_fixtures += quantity_by_api["count_fixture"]
                            p_api_useFixtures += quantity_by_api["count_usefixture"]
                            p_api_genericMark += quantity_by_api["count_genericMark"]
                            p_api_genericPytest += quantity_by_api["count_genericPytest"]

            apis_in_commit = {
                "commit_index": commit["commit_index"],
                "author_email": commit["author_email"],
                "date": commit["date"],
                "commit_hash": commit["commit_hash"],

                "test_files": test_files,
                "test_methods": test_methods,

                "u_api_testCaseSubclasses": u_api_testCaseSubclasses,
                "u_api_asserts": u_api_asserts,
                "u_api_setUps": u_api_setUps,
                "u_api_setUpClasses": u_api_setUpClasses,
                "u_api_tearDown": u_api_tearDown,
                "u_api_tearDownClasses": u_api_tearDownClasses,
                "u_api_unittestSkiptests": u_api_unittestSkiptests,
                "u_api_selfSkiptests": u_api_selfSkiptests,
                "u_api_expectedFailures": u_api_expectedFailures,

                "native_asserts": native_asserts,
                "p_api_pytestRaises": p_api_pytestRaises,
                "p_api_simpleSkips": p_api_simpleSkips,
                "p_api_markSkips": p_api_markSkips,
                "p_api_expectedFailures": p_api_expectedFailures,
                "p_api_fixtures": p_api_fixtures,
                "p_api_useFixtures": p_api_useFixtures,
                "p_api_genericMark": p_api_genericMark,
                "p_api_genericPytest": p_api_genericPytest,
            }

            apis_info.append(apis_in_commit)

        if os.path.exists(self.local_path_to_repo) and os.path.isdir(self.local_path_to_repo):
            shutil.rmtree(self.local_path_to_repo)

        return apis_info

from git import Repo
from pyparsing import Keyword, QuotedString, pythonStyleComment, quotedString

from heuristics.test_methods import TestMethodsHeuristics as mh
from heuristics.apis import UnittestAPIHeuristics as uAPIh, PytestAPIHeuristics as pAPIh

docString = QuotedString(quoteChar='"""', multiline=True, unquoteResults=False)

class CheckoutsAnalyzer:
    @classmethod
    def process_checkouts(cls, repo_url, commits):
    local_path_to_repo = repo_url.split('/')[-1]
    repo = Repo.clone_from(repo_url, local_path_to_repo)
    apis_info = []

    for commit in commits:
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

                        content = (cppStyleComment|pythonStyleComment|quotedString|docString).suppress().transformString(content)

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

        apis_info.append(apis_in_commit)

    if os.path.exists(local_path_to_repo) and os.path.isdir(local_path_to_repo):
        shutil.rmtree(local_path_to_repo)

    return apis_info

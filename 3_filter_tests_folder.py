import re
from pydriller import RepositoryMining


PATH_FOLDER_REGEX = "^tests/*"
PYTEST_REGEX = "import pytest"

def is_a_test_file(path):
    return re.search(PATH_FOLDER_REGEX, path) != None

def use_pytest(code):
    return re.search(PYTEST_REGEX, code) != None


print("\n")
print("Remote repository - Flask")
for commit in RepositoryMining("https://github.com/pallets/flask", single="b724832872ae4b4cd4b5f61c153eae39f1c3b213").traverse_commits():
# for commit in RepositoryMining("https://github.com/pallets/flask", only_in_branch="master", only_no_merge=True).traverse_commits():
    print("Commit {}, author {}".format(commit.hash, commit.author.name))
    for modification in commit.modifications:
        print('{} is a test file? {}'.format(modification.new_path, is_a_test_file(modification.new_path)))

        if is_a_test_file(modification.new_path):
            print('\tFile: {}\t Imports pytest: {}'.format(modification.new_path, use_pytest(modification.source_code)))

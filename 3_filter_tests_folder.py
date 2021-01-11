import re
from pydriller import RepositoryMining


PATH_FOLDER_REGEX = "^[tests/].*[.py]$"
PYTEST_REGEX = "import pytest"

def is_a_test_file(path):
    return path != None and re.search(PATH_FOLDER_REGEX, path) != None

def check_pytest(code):
    return code != None and re.search(PYTEST_REGEX, code) != None

first_occurrence = {}

print("\n")
print("Remote repository - Flask - single commit")
for commit in RepositoryMining("https://github.com/pallets/flask", single="eb41e7e417cbf53d19517e356381423cfd256c2f").traverse_commits():
    print("Commit {}, author {}".format(commit.hash, commit.author.name))
    for modification in commit.modifications:
        # print('\t{} is a test file? {}'.format(modification.new_path, is_a_test_file(modification.new_path)))

        if is_a_test_file(modification.new_path):
            print('\t\tFile: {}\t imports pytest? {}'.format(modification.new_path, check_pytest(modification.source_code)))


print("\n")
print("Remote repository - Flask")
for commit in RepositoryMining("https://github.com/pallets/flask", only_in_branch="master", only_no_merge=True).traverse_commits():
    for modification in commit.modifications:
        # print('\t{} is a test file? {}'.format(modification.new_path, is_a_test_file(modification.new_path)))

        if is_a_test_file(modification.new_path):
            print("Commit {}, author {} ({})".format(commit.hash, commit.author.name, commit.author_date))
            uses_pytest = check_pytest(modification.source_code)

            print('\t\tDoes the file: {}\t imports pytest? {}'.format(modification.new_path, uses_pytest))
            if not first_occurrence and uses_pytest:
                first_occurrence = {
                    "file": modification.new_path,
                    "author": commit.author.name,
                    "date": commit.author_date,
                    "commit_hash": commit.hash,
                    "commit_message": commit.msg,
                }

print("The first occurence of pytest was:")
print(first_occurrence)

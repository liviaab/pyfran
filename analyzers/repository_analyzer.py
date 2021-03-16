import os
import sys
from heuristics.file import FileHeuristics
from heuristics.pytest import PytestHeuristics
from heuristics.unittest import UnittestHeuristics
from analyzers.github_service import GithubService

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

class RepositoryAnalyzer:
    def __init__(self, repo_url):
        self.repo_org = repo_url.split('/')[-2]
        self.repo_name = repo_url.split('/')[-1]
        self.gh_service = GithubService()
        self.usesUnittest = False
        self.usesPytest = False

    def search_frameworks(self):
        root_folder = self.gh_service.clone_repository(self.repo_org, self.repo_name)
        self.__examine_repository(root_folder)
        self.gh_service.remove_local_repository(self.repo_org, self.repo_name)

    def __examine_repository(self, root_folder):
        walk_dir = os.path.abspath(root_folder)

        for currentpath, folders, files in os.walk(walk_dir):
            for file in files:
                name, extension = os.path.splitext(file)
                if extension not in VALID_EXTENSIONS:
                    continue

                with open(os.path.join(currentpath, file), 'r') as src:
                    content = src.read()
                    if UnittestHeuristics.matches_a(content):
                        self.usesUnittest = True

                    if PytestHeuristics.matches_a(content):
                        self.usesPytest = True

            if self.usesUnittest and self.usesPytest:
                return

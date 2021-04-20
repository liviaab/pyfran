import os
import sys

from heuristics.pytest import PytestHeuristics
from heuristics.unittest import UnittestHeuristics
from analyzers.github_service import GithubService

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

def examine_local_repository(root_folder):
    usesUnittest = False
    usesPytest = False
    walk_dir = os.path.abspath(root_folder)

    for currentpath, _folders, files in os.walk(walk_dir):
        for file in files:
            _name, extension = os.path.splitext(file)
            if extension not in VALID_EXTENSIONS:
                continue

            with open(os.path.join(currentpath, file), 'r') as src:
                content = src.read()
                if UnittestHeuristics.matches_a(content):
                    usesUnittest = True

                if PytestHeuristics.matches_a(content):
                    usesPytest = True

        if usesUnittest and usesPytest:
            break

    return (usesUnittest, usesPytest)

class RepositoryAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.is_local = False if repo_url.startswith('http') else True
        self.usesUnittest = False
        self.usesPytest = False

    def search_frameworks(self):
        service = RemoteRepositoryAnalyzer(self.repo_url)

        if (self.is_local):
            service = LocalRepositoryAnalyzer(self.repo_url)

        usesUnittest, usesPytest = service.search_frameworks()

        self.usesUnittest = usesUnittest
        self.usesPytest = usesPytest


class LocalRepositoryAnalyzer:
    def __init__(self, path):
        self.path = path

    def search_frameworks(self):
        usesUnittest, usesPytest = examine_local_repository(self.path)
        return (usesUnittest, usesPytest)

class RemoteRepositoryAnalyzer:
    def __init__(self, url):
        self.url = url
        self.repo_org = url.split('/')[-2]
        self.repo_name = url.split('/')[-1]

    def search_frameworks(self):
        gh_service = GithubService()

        root_folder = gh_service.clone_repository(self.repo_org, self.repo_name)
        usesUnittest, usesPytest = examine_local_repository(root_folder)
        gh_service.remove_local_repository(self.repo_org, self.repo_name)
        return (usesUnittest, usesPytest)

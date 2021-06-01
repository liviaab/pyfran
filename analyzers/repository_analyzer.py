import os
import sys
import shutil

from heuristics.pytest import PytestHeuristics
from heuristics.unittest import UnittestHeuristics
from analyzers.github_service import GithubService

from datetime import datetime

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

def examine_local_repository(root_folder):
    usesUnittest = False
    usesPytest = False
    nof_unittest = 0
    nof_pytest = 0
    nof_both = 0
    walk_dir = os.path.abspath(root_folder)

    for currentpath, _folders, files in os.walk(walk_dir):
        for file in files:
            _name, extension = os.path.splitext(file)
            if extension not in VALID_EXTENSIONS:
                continue

            with open(os.path.join(currentpath, file), 'r') as src:
                try:
                    content = src.read()
                    if UnittestHeuristics.matches_a(content):
                        usesUnittest = True
                        nof_unittest += 1

                    if PytestHeuristics.matches_a(content):
                        usesPytest = True
                        nof_pytest +=1

                    if UnittestHeuristics.matches_a(content) and PytestHeuristics.matches_a(content):
                        nof_both += 1
                except:
                    print("Something went wrong at {}".format(os.path.join(currentpath, file)))

    return (usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both)

def count_local_files(root_folder):
    number_of_files = 0
    walk_dir = os.path.abspath(root_folder)
    excluded_folders = ['.git']

    for _currentpath, folders, files in os.walk(walk_dir, topdown=True):
        folders[:] = [ f for f in folders if f not in excluded_folders ]
        number_of_files += len(files)

    return number_of_files

class RepositoryAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.is_local = False if repo_url.startswith('http') else True
        self.service =  LocalRepositoryAnalyzer(self.repo_url) if self.is_local else RemoteRepositoryAnalyzer(self.repo_url)
        self.usesUnittest = False
        self.usesPytest = False
        self.nof_unittest = 0
        self.nof_pytest = 0
        self.nof_both = 0

    def search_frameworks(self):
        usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both = self.service.search_frameworks()

        self.usesUnittest = usesUnittest
        self.usesPytest = usesPytest
        self.nof_unittest = nof_unittest
        self.nof_pytest = nof_pytest
        self.nof_both = nof_both
    
    def count_files(self):
        nof = self.service.count_files()
        return nof

class LocalRepositoryAnalyzer:
    def __init__(self, path):
        self.path = path

    def search_frameworks(self):
        usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both = examine_local_repository(self.path)
        return (usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both)
    
    def count_files(self):
        nof = count_local_files(self.path)
        return nof


class RemoteRepositoryAnalyzer:
    def __init__(self, url):
        self.url = url
        self.repo_org = url.split('/')[-2]
        self.repo_name = url.split('/')[-1]

    def search_frameworks(self):
        gh_service = GithubService()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Time marker #6 - Clone repo", dt_string)
        root_folder = gh_service.clone_repository(self.repo_org, self.repo_name)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Time marker #7 - Examine local repo", dt_string)
        usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both = examine_local_repository(root_folder)
        gh_service.remove_local_repository(self.repo_org, self.repo_name)
        return (usesUnittest, usesPytest, nof_unittest, nof_pytest, nof_both)

    def count_files(self):
        gh_service = GithubService()

        root_folder = gh_service.clone_repository(self.repo_org, self.repo_name)
        nof = count_local_files(root_folder)
        gh_service.remove_local_repository(self.repo_org, self.repo_name)
        return nof

from analyzers.github_service import GithubService

class RepositoryAnalyzer:
    def __init__(self, repo_url):

        self.repo_org = repo_url.split('/')[-2]
        self.repo_name = repo_url.split('/')[-1]
        self.gh_service = GithubService()
        self.unittestResults = {}
        self.pytestResults = {}

    def search_frameworks(self):
        self.__search_for_unittest()
        self.__search_for_pytest()

    def usesUnittest(self):
        return self.unittestResults["total_count"] and self.unittestResults["total_count"] > 0

    def usesPytest(self):
        return self.pytestResults["total_count"] and self.pytestResults["total_count"] > 0

    def __search_for_unittest(self):
        query = "?q=unittest+in:file+repo:{}/{}".format(self.repo_org, self.repo_name)

        jsonResponse = self.gh_service.search_code(query)
        self.unittestResults = jsonResponse

    def __search_for_pytest(self):
        query = "?q=pytest+in:file+repo:{}/{}".format(self.repo_org, self.repo_name)

        jsonResponse = self.gh_service.search_code(query)
        self.pytestResults = jsonResponse

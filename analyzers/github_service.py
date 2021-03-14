import requests

class GithubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.default_headers = {
            "Accept": "application/vnd.github.v3+json"
        }

    def search_code(self, query, custom_headers={}):
        path = "/search/code"
        final_headers = {**self.default_headers, **custom_headers}

        response = requests.get(
            self.base_url + path + query,
            headers=final_headers
        )

        if response.status_code != 200:
            raise Exception("Failed to query Github API")

        return response.json()

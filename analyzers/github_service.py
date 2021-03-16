import os
import shutil
import zipfile
import requests

class GithubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.default_headers = {
            "Accept": "application/vnd.github.v3+json"
        }

    def clone_repository(self, org, name, custom_headers={}):
        final_headers = {**self.default_headers, **custom_headers}

        response = requests.get(
            self.base_url + "/repos/{}/{}/zipball".format(org, name),
            headers=final_headers,
            stream=True
        )

        if response.status_code != 200:
            raise Exception("Failed to query Github API")

        zip_path = "{}-{}.zip".format(org, name)
        with open(zip_path, "wb") as fd:
            for chunk in response.iter_content(chunk_size=512):
                fd.write(chunk)

        filepath = "{}-{}".format(org, name)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(filepath)

        os.remove(zip_path)
        print("Downloaded Repo")
        return filepath

    def remove_local_repository(self, org, name):
        filepath = "{}-{}".format(org, name)

        if os.path.exists(filepath) and os.path.isdir(filepath):
            shutil.rmtree(filepath)

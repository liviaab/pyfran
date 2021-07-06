# PyFrAn

The main goal of **Py**thon **Fr**amework **An**alyzer is to determine a class (pytest, unittest, ongoing, migrated, unknown) for a python project.

## Requirements

`pip v3`

`python 3.7`

## Running locally
```sh
$ sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
$ pip3 install -r requirements.txt
$ python3 main.py -i in.csv
```

## Details
Given a list of local or remote URLs projects, PyFrAn determines the class of each repository and generates intermediate csvs with information related to the commits, test APIs and commit authors. We can say that, for each repository, it needs 4 steps to complete this:
1. Traverse the list of diffs for each commit
2. Check out every 5 commits to store information on accumulated API usage
3. Verify the current state of the repo
4. Assign a class (pytest, unittest, ongoing, migrated, unknown)
5. Generate three csv files containing information about:
    - authors and migration authors ([repository-name]_authors.csv)
    - accumulated API usage (every 5 commits) ([repository-name]_api.csv)
    - and API usage in every commit  ([repository-name]_commit.csv)

After analyzing all the projects, we aggregate some informations in the `metrics_per_category.csv` file.

During step #1 we:
- Verify if there was an addition or removal of a `unittest` or `pytest` reference ([unittest](https://github.com/liviaab/pyfran/blob/b62a6a3ac7cb318ef2770d254805a14bb9c26417/heuristics/unittest.py) and [pytest](https://github.com/liviaab/pyfran/blob/b62a6a3ac7cb318ef2770d254805a14bb9c26417/heuristics/pytest.py) heuristics)
- Verify if there was an addition or removal of the chosen APIs ([apis](https://github.com/liviaab/pyfran/blob/b62a6a3ac7cb318ef2770d254805a14bb9c26417/heuristics/apis.py) heuristics)
- Verify if we can attribute tags to the commit and set it as an "commit of interest" ([rules](https://github.com/liviaab/pyfran/blob/b62a6a3ac7cb318ef2770d254805a14bb9c26417/analyzers/delta_commits_analyzer.py#L255) to define a tag)

We need to execute step #3 because, if during step#1 we conclude that the repository has references to both unittest and pytest, we still need information to determine whether the repository is 'migrated' or 'ongoing'. The rules to define each class are described [here](https://github.com/liviaab/pyfran/blob/b62a6a3ac7cb318ef2770d254805a14bb9c26417/classifiers/main_classifier.py#L117)

With the information collected in the first three steps, we can finally generate the csv files.

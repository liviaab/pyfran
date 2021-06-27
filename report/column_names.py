def author_columns():
    return [
        "email",
        "total_commits",
        "migration_contributor",
        "migration_commits"
    ]

def commit_columns(): 
    return [
        "commit_index",
        "author_name",
        "author_email",
        "date",
        "commit_hash",
        "files_changed",
        "are_we_interested",
        "pytest_in_added_diffs",
        "pytest_in_removed_diffs",
        "has_test_file",
        "unittest_in_code",
        "unittest_in_removed_diffs",
        "pytest_in_code",
        "tags",

        "u_count_added_testCaseSubclass",
        "u_count_added_assert",
        "u_count_added_setUp",
        "u_count_added_setUpClass",
        "u_count_added_tearDown",
        "u_count_added_tearDownClass",
        "u_count_added_unittestSkipTest",
        "u_count_added_selfSkipTest",
        "u_count_added_expectedFailure",
        "u_count_added_unittestMock",

        "u_count_removed_testCaseSubclass",
        "u_count_removed_assert",
        "u_count_removed_setUp",
        "u_count_removed_setUpClass",
        "u_count_removed_tearDown",
        "u_count_removed_tearDownClass",
        "u_count_removed_unittestSkipTest",
        "u_count_removed_selfSkipTest",
        "u_count_removed_expectedFailure",
        "u_count_removed_unittestMock",

        "p_count_added_native_assert",
        "p_count_added_pytestRaise",
        "p_count_added_simpleSkip",
        "p_count_added_markSkip",
        "p_count_added_expectedFailure",
        "p_count_added_fixture",
        "p_count_added_usefixture",
        "p_count_added_genericMark",
        "p_count_added_genericPytest",

        "p_count_removed_native_assert",
        "p_count_removed_pytestRaise",
        "p_count_removed_simpleSkip",
        "p_count_removed_markSkip",
        "p_count_removed_expectedFailure",
        "p_count_removed_fixture",
        "p_count_removed_usefixture",
        "p_count_removed_genericMark",
        "p_count_removed_genericPytest",

        "unittest_matches_in_added_lines",
        "unittest_matches_in_removed_lines",
        "pytest_matches_in_added_lines",
        "pytest_matches_in_removed_lines",

        "commit_message"
    ]

def api_columns():
    return [
        "commit_index",
        "author_email",
        "date",
        "commit_hash",

        "test_files",
        "test_methods",

        "u_api_testCaseSubclasses",
        "u_api_asserts",
        "u_api_setUps",
        "u_api_setUpClasses",
        "u_api_tearDown",
        "u_api_tearDownClasses",
        "u_api_unittestSkiptests",
        "u_api_selfSkiptests",
        "u_api_expectedFailures",

        "native_asserts",
        "p_api_pytestRaises",
        "p_api_simpleSkips",
        "p_api_markSkips",
        "p_api_expectedFailures",
        "p_api_fixtures",
        "p_api_useFixtures",
        "p_api_genericMark",
        "p_api_genericPytest",
    ]

def repository_columns():
    return [
        "CATEGORY",
        "REPOSITORY_NAME",
        "REPOSITORY_LINK",
        "NOC",
        "NOC_UNITTEST",
        "NOC_PYTEST",
        "NOC_BOTH",
        "OCM",
        "NOA (name)",
        "NOMA (name)",
        "NOMAP (name)",
        "NOA (email)",
        "NOMA (email)",
        "NOMAP (email)",
        "NOA email - name",
        "NOD",
        "NOF",
        "NOF_UNITTEST",
        "NOF_PYTEST",
        "NOF_BOTH",
        "PBU",
        "FC_UNITTEST",
        "FC_PYTEST",
        "FC_UNITTEST_LINK",
        "FC_PYTEST_LINK",
        "LC_UNITTEST",
        "LC_PYTEST",
        "LC_UNITTEST_LINK",
        "LC_PYTEST_LINK"
    ]

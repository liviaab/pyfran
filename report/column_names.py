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
        "pytest_in_removed_diffs",
        "has_test_file",
        "unittest_in_code",
        "unittest_in_removed_diffs",
        "pytest_in_code",

        "count_added_testCaseSubclass",
        "count_added_assert",
        "count_added_setUp",
        "count_added_setUpClass",
        "count_added_tearDown",
        "count_added_tearDownClass",
        "count_added_unittestSkipTest",
        "count_added_selfSkipTest",
        "count_added_expectedFailure",

        "count_removed_testCaseSubclass",
        "count_removed_assert",
        "count_removed_setUp",
        "count_removed_setUpClass",
        "count_removed_tearDown",
        "count_removed_tearDownClass",
        "count_removed_unittestSkipTest",
        "count_removed_selfSkipTest",
        "count_removed_expectedFailure",

        "count_added_native_assert",
        "count_added_raise",
        "count_added_pytestRaise",
        "count_added_simpleSkip",
        "count_added_markSkip",
        "count_added_expectedFailure",
        "count_added_fixture",
        "count_added_usefixture",
        "count_added_generalMark",
        "count_added_generalPytest",

        "count_removed_native_assert",
        "count_removed_raise",
        "count_removed_pytestRaise",
        "count_removed_simpleSkip",
        "count_removed_markSkip",
        "count_removed_expectedFailure",
        "count_removed_fixture",
        "count_removed_usefixture",
        "count_removed_generalMark",
        "count_removed_generalPytest",

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
        "p_api_raises",
        "p_api_pytestRaises",
        "p_api_simpleSkips",
        "p_api_markSkips",
        "p_api_expectedFailures",
        "p_api_fixtures",
        "p_api_useFixtures",
        "p_api_generalMark",
        "p_api_generalpytest",
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

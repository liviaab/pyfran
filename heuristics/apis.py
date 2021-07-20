import re

class UnittestAPIHeuristics:
    testCaseSubclass_pattern = "(class\s+.*\([unittest\.]*TestCase.*\):)"
    assert_pattern = "self.assert(\w*)(.*)"  # self.assert([^_]\w*)(.*)
    setUp_pattern = "def\s+setUp\(.*\):"
    setUpClass_pattern = "def\s+setUp(\w+)(\(.*\)):" # setUpClass | setUpModule
    tearDown_pattern = "def\s+tearDown\(.*\):"
    tearDownClass_pattern = "def\s+tearDown(\w+)(\(.*\)):" # tearDownClass | tearDownModule
    unittestSkipTest_pattern = "[@]{0,1}unittest.skip.*?\((.*)" # @unittest.skip | @unittest.skipIf | @unittest.skipUnless
    selfSkipTest_pattern = "[self.s|unittest.S]kipTest(\(.*)" # self.skipTest() | unittest.SkipTest()
    expectedFailure_pattern = "@unittest.expectedFailure"
    unittestMock_pattern = "(\s+unittest.mock\s+)"
    unittestImport_pattern = "(import\s+unittest)"

    @classmethod
    def check_apis(cls, content):
        matches_testCaseSubclass = re.findall(cls.testCaseSubclass_pattern, content)
        matches_assert = re.findall(cls.assert_pattern, content)
        matches_setUp = re.findall(cls.setUp_pattern, content)
        matches_setUpClass = re.findall(cls.setUpClass_pattern, content)
        matches_tearDown = re.findall(cls.tearDown_pattern, content)
        matches_tearDownClass = re.findall(cls.tearDownClass_pattern, content)
        matches_unittestSkipTest = re.findall(cls.unittestSkipTest_pattern, content)
        matches_selfSkipTest = re.findall(cls.selfSkipTest_pattern, content)
        matches_expectedFailure = re.findall(cls.expectedFailure_pattern, content)
        matches_unittestMock = re.findall(cls.unittestMock_pattern, content)
        matches_unittestImport = re.findall(cls.unittestImport_pattern, content)

        quantity_by_api = {
            "count_testCaseSubclass": len(matches_testCaseSubclass),
            "count_assert": len(matches_assert),
            "count_setUp": len(matches_setUp),
            "count_setUpClass": len(matches_setUpClass),
            "count_tearDown": len(matches_tearDown),
            "count_tearDownClass": len(matches_tearDownClass),
            "count_unittestSkipTest": len(matches_unittestSkipTest),
            "count_selfSkipTest": len(matches_selfSkipTest),
            "count_expectedFailure": len(matches_expectedFailure),
            "count_unittestMock": len(matches_unittestMock),
            "count_unittestImport": len(matches_unittestImport),

            "matches_testCaseSubclass": matches_testCaseSubclass,
            "matches_assert": matches_assert,
            "matches_setUp": matches_setUp,
            "matches_setUpClass": matches_setUpClass,
            "matches_tearDown": matches_tearDown,
            "matches_tearDownClass": matches_tearDownClass,
            "matches_unittestSkipTest": matches_unittestSkipTest,
            "matches_selfSkipTest": matches_selfSkipTest,
            "matches_expectedFailure": matches_expectedFailure,
            "matches_unittestMock": matches_unittestMock,
            "matches_unittestImport": matches_unittestImport,
        }

        return quantity_by_api

    @classmethod
    def check_apis_in_list(cls, contents):
        quantity_by_api = {
            "count_testCaseSubclass": 0,
            "count_assert": 0,
            "count_setUp": 0,
            "count_setUpClass": 0,
            "count_tearDown": 0,
            "count_tearDownClass": 0,
            "count_unittestSkipTest": 0,
            "count_selfSkipTest": 0,
            "count_expectedFailure": 0,
            "count_unittestMock": 0,
            "count_unittestImport": 0,

            "matches_testCaseSubclass": [],
            "matches_assert": [],
            "matches_setUp": [],
            "matches_setUpClass": [],
            "matches_tearDown": [],
            "matches_tearDownClass": [],
            "matches_unittestSkipTest": [],
            "matches_selfSkipTest": [],
            "matches_expectedFailure": [],
            "matches_unittestMock": [],
            "matches_unittestImport": [],
        }

        for content in contents:
            if content.strip().startswith('#') or content.strip().startswith('"""'):
                continue

            tmp = cls.check_apis(content)
            quantity_by_api = {
                "count_testCaseSubclass": quantity_by_api["count_testCaseSubclass"] + tmp["count_testCaseSubclass"],
                "count_assert": quantity_by_api["count_assert"] + tmp["count_assert"],
                "count_setUp": quantity_by_api["count_setUp"] + tmp["count_setUp"],
                "count_setUpClass": quantity_by_api["count_setUpClass"] + tmp["count_setUpClass"],
                "count_tearDown": quantity_by_api["count_tearDown"] + tmp["count_tearDown"],
                "count_tearDownClass": quantity_by_api["count_tearDownClass"] + tmp["count_tearDownClass"],
                "count_unittestSkipTest": quantity_by_api["count_unittestSkipTest"] + tmp["count_unittestSkipTest"],
                "count_selfSkipTest": quantity_by_api["count_selfSkipTest"] + tmp["count_selfSkipTest"],
                "count_expectedFailure": quantity_by_api["count_expectedFailure"] + tmp["count_expectedFailure"],
                "count_unittestMock": quantity_by_api["count_unittestMock"] + tmp["count_unittestMock"],
                "count_unittestImport": quantity_by_api["count_unittestImport"] + tmp["count_unittestImport"],

                "matches_testCaseSubclass": quantity_by_api["matches_testCaseSubclass"] + tmp["matches_testCaseSubclass"],
                "matches_assert": quantity_by_api["matches_assert"] + tmp["matches_assert"],
                "matches_setUp": quantity_by_api["matches_setUp"] + tmp["matches_setUp"],
                "matches_setUpClass": quantity_by_api["matches_setUpClass"] + tmp["matches_setUpClass"],
                "matches_tearDown": quantity_by_api["matches_tearDown"] + tmp["matches_tearDown"],
                "matches_tearDownClass": quantity_by_api["matches_tearDownClass"] + tmp["matches_tearDownClass"],
                "matches_unittestSkipTest": quantity_by_api["matches_unittestSkipTest"] + tmp["matches_unittestSkipTest"],
                "matches_selfSkipTest": quantity_by_api["matches_selfSkipTest"] + tmp["matches_selfSkipTest"],
                "matches_expectedFailure": quantity_by_api["matches_expectedFailure"] + tmp["matches_expectedFailure"],
                "matches_unittestMock": quantity_by_api["matches_unittestMock"] + tmp["matches_unittestMock"],
                "matches_unittestImport": quantity_by_api["matches_unittestImport"] + tmp["matches_unittestImport"],
            }

        return quantity_by_api


class PytestAPIHeuristics:
    native_assert_pattern = "\s*assert\s+(.*)"
    pytestRaise_pattern = "pytest.raises(\(.*\))"
    simpleSkip_pattern = "pytest.skip(\(.*\))"
    markSkip_pattern = "[@]?pytest.mark.skip(.*\(.*\))?"
    expectedFailure_pattern = "[@]?pytest.mark.xfail(\(.*\))?"
    fixture_pattern = "@pytest.fixture(.*)"
    usefixture_pattern = "@pytest.mark.usefixtures(\(.*\))?"
    parametrize_pattern = "@pytest.mark.parametrize(\(.*\))?"
    genericMark_pattern = "[@]?pytest.mark\.(.*)(\(.*)" 
    genericPytest_pattern = "@pytest\.(.*)"
    monkeypatch_pattern = "\s*monkeypatch\.(.*)"
    pytestmock_pattern = "(pytest-mock)"
    pytesImport_pattern = "(import\s+pytest)"

    @classmethod
    def check_apis(cls, content):
        matches_native_assert = re.findall(cls.native_assert_pattern, content)
        matches_pytestRaise = re.findall(cls.pytestRaise_pattern, content)
        matches_simpleSkip = re.findall(cls.simpleSkip_pattern, content)
        matches_markSkip = re.findall(cls.markSkip_pattern, content)
        matches_expectedFailure = re.findall(cls.expectedFailure_pattern, content)
        matches_fixture = re.findall(cls.fixture_pattern, content)
        matches_usefixture = re.findall(cls.usefixture_pattern, content)
        matches_parametrize = re.findall(cls.parametrize_pattern, content)
        matches_genericMark = re.findall(cls.genericMark_pattern, content)
        matches_genericPytest = re.findall(cls.genericPytest_pattern, content)
        matches_monkeypatch = re.findall(cls.monkeypatch_pattern, content)
        matches_pytestmock = re.findall(cls.pytestmock_pattern, content)
        matches_pytestImport = re.findall(cls.pytesImport_pattern, content)

        quantity_by_api = {
            "count_native_assert": len(matches_native_assert),
            "count_pytestRaise": len(matches_pytestRaise),
            "count_simpleSkip": len(matches_simpleSkip),
            "count_markSkip": len(matches_markSkip),
            "count_expectedFailure": len(matches_expectedFailure),
            "count_fixture": len(matches_fixture),
            "count_usefixture": len(matches_usefixture),
            "count_parametrize": len(matches_parametrize),
            "count_genericMark": len(matches_genericMark),
            "count_genericPytest": len(matches_genericPytest),
            "count_monkeypatch": len(matches_monkeypatch),
            "count_pytestmock": len(matches_pytestmock),
            "count_pytestImport": len(matches_pytestImport),

            "matches_native_assert": matches_native_assert,
            "matches_pytestRaise": matches_pytestRaise,
            "matches_simpleSkip": matches_simpleSkip,
            "matches_markSkip": matches_markSkip,
            "matches_expectedFailure": matches_expectedFailure,
            "matches_fixture": matches_fixture,
            "matches_usefixture": matches_usefixture,
            "matches_parametrize": matches_parametrize,
            "matches_genericMark": matches_genericMark,
            "matches_genericPytest": matches_genericPytest,
            "matches_monkeypatch": matches_monkeypatch,
            "matches_pytestmock": matches_pytestmock,
            "matches_pytestImport": matches_pytestImport,
        }

        return quantity_by_api

    @classmethod
    def check_apis_in_list(cls, contents):
        quantity_by_api = {
            "count_native_assert": 0,
            "count_pytestRaise": 0,
            "count_simpleSkip": 0,
            "count_markSkip": 0,
            "count_expectedFailure": 0,
            "count_fixture": 0,
            "count_usefixture": 0,
            "count_parametrize": 0,
            "count_genericMark": 0,
            "count_genericPytest": 0,
            "count_monkeypatch": 0,
            "count_pytestmock": 0,
            "count_pytestImport": 0,

            "matches_native_assert": [],
            "matches_pytestRaise": [],
            "matches_simpleSkip": [],
            "matches_markSkip": [],
            "matches_expectedFailure": [],
            "matches_fixture": [],
            "matches_usefixture": [],
            "matches_parametrize": [],
            "matches_genericMark": [],
            "matches_genericPytest": [],
            "matches_monkeypatch": [],
            "matches_pytestmock": [],
            "matches_pytestImport": [],
        }

        for content in contents:
            if content.strip().startswith('#') or content.strip().startswith('"""'):
                continue

            tmp = cls.check_apis(content)
            quantity_by_api = {
                "count_native_assert": quantity_by_api["count_native_assert"] + tmp["count_native_assert"],
                "count_pytestRaise": quantity_by_api["count_pytestRaise"] + tmp["count_pytestRaise"],
                "count_simpleSkip": quantity_by_api["count_simpleSkip"] + tmp["count_simpleSkip"],
                "count_markSkip": quantity_by_api["count_markSkip"] + tmp["count_markSkip"],
                "count_expectedFailure": quantity_by_api["count_expectedFailure"] + tmp["count_expectedFailure"],
                "count_fixture": quantity_by_api["count_fixture"] + tmp["count_fixture"],
                "count_usefixture": quantity_by_api["count_usefixture"] + tmp["count_usefixture"],
                "count_parametrize": quantity_by_api["count_parametrize"] + tmp["count_parametrize"],
                "count_genericMark": quantity_by_api["count_genericMark"] + tmp["count_genericMark"],
                "count_genericPytest": quantity_by_api["count_genericPytest"] + tmp["count_genericPytest"],
                "count_monkeypatch": quantity_by_api["count_monkeypatch"] + tmp["count_monkeypatch"],
                "count_pytestmock": quantity_by_api["count_pytestmock"] + tmp["count_pytestmock"],
                "count_pytestImport": quantity_by_api["count_pytestImport"] + tmp["count_pytestImport"],

                "matches_native_assert": quantity_by_api["matches_native_assert"] + tmp["matches_native_assert"],
                "matches_pytestRaise": quantity_by_api["matches_pytestRaise"] + tmp["matches_pytestRaise"],
                "matches_simpleSkip": quantity_by_api["matches_simpleSkip"] + tmp["matches_simpleSkip"],
                "matches_markSkip": quantity_by_api["matches_markSkip"] + tmp["matches_markSkip"],
                "matches_expectedFailure": quantity_by_api["matches_expectedFailure"] + tmp["matches_expectedFailure"],
                "matches_fixture": quantity_by_api["matches_fixture"] + tmp["matches_fixture"],
                "matches_usefixture": quantity_by_api["matches_usefixture"] + tmp["matches_usefixture"],
                "matches_parametrize": quantity_by_api["matches_parametrize"] + tmp["matches_parametrize"],
                "matches_genericMark": quantity_by_api["matches_genericMark"] + tmp["matches_genericMark"],
                "matches_genericPytest": quantity_by_api["matches_genericPytest"] + tmp["matches_genericPytest"],
                "matches_monkeypatch": quantity_by_api["matches_monkeypatch"] + tmp["matches_monkeypatch"],
                "matches_pytestmock": quantity_by_api["matches_pytestmock"] + tmp["matches_pytestmock"],
                "matches_pytestImport": quantity_by_api["matches_pytestImport"] + tmp["matches_pytestImport"],
            }

        return quantity_by_api

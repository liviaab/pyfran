import re

TESTPATH_REGEX = "(test)"       # Tem `test` em algumm lugar do nome:
                                # src/test/test_one.py
                                # src/modules/test_one.py


def is_a_test_file(path):
    print(re.search(TESTPATH_REGEX, path))
    return path != None and re.search(TESTPATH_REGEX, path) != None


CONFIG_REGEX = "(.*requirements\..*)"
CONFIG_REGEX += "|(setup.py)"
CONFIG_REGEX += "|(README\..*)"
CONFIG_REGEX += "|(pytest.ini)"
CONFIG_REGEX += "|(pyproject.toml)"
CONFIG_REGEX += "|(tox.ini)"
CONFIG_REGEX += "|(setup.cfg)"
CONFIG_REGEX += "|(\..*-ci\..*)"
CONFIG_REGEX += "|(config\..*)"

def is_a_config_file(path):
    """
        Arquivos de configuração ou scripts. Exemplos:
        requirements.txt, setup.py, README.md/README.txt, pytest.ini, pyproject.toml, tox.ini, setup.cfg
        .gitlab-ci.[yml|yaml] .travis-ci.[yml|yaml] config.yml
    """
    print(re.search(TESTPATH_REGEX, path))
    return path != None and re.search(TESTPATH_REGEX, path) != None

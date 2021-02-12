# Unittest

[From unittest docs](https://docs.python.org/3/library/unittest.html)

_A testcase is created by subclassing unittest.TestCase._ (...) To make your own test cases you **must** write subclasses of TestCase or use FunctionTestCase.
- Subclasses dessas subclasses também são válidas
- Métodos de teste iniciam com as letras `test`
- Pattern to match test files (test*.py default)
- Para rodar os testes, colocar no arquivo
 ```python
 if __name__ == '__main__':
     unittest.main()

 ```
 - Unittest supports simple test discovery. In order to be compatible with test discovery, all of the test files must be modules or packages (including namespace packages) importable from the top-level directory of the project
- Nome de classe: não tem padrão. Exemplos da doc: `DefaultWidgetSizeTestCase`, `TestStringMethods`

Como é possível executar:
```sh
python nome_do_arquivo_de_teste.py
python -m unittest test_module1 test_module2
python -m unittest test_module.TestClass
python -m unittest test_module.TestClass.test_method
python -m unittest tests/test_something.py
python -m unittest discover
```
https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure

[Python 2.7] This document is for an old version of Python that is no longer supported. You should upgrade and read the Python documentation for the current stable release. (3.9.1)


# Pytest

[Da documentação](https://docs.pytest.org/en/stable/)

Primeiramente, deve-se instalar o pacote:
```sh
pip install -U pytest
```

_You can also gradually move away from subclassing from unittest.TestCase to plain asserts and then start to benefit from the full pytest feature set step by step._

Como é possível executar:
```sh
pytest _test_folder
```

Como é possível identificar se um projeto está usando pytest ou não
- Se estiver presente em arquivos que contém descrição de requisitos
(requirements.txt, setup.py, README.md/README.txt, pytest.ini, pyproject.toml, tox.ini or setup.cfg)
- Se algum arquivo de script tiver uma linha que roda o pytest (.gitlab-ci.* .travis-ci.* ...)
- Arquivos com nomes no formato `test_*.py` ou `*_test.py` n[fonte](https://docs.pytest.org/en/stable/getting-started.html)
- Funções que começam com test_
- Se os testes forem definidos como métodos em uma classes, esta deve ter o nome iniciado com Test

Convenções do `pytest` para descobrimento de teste em Python  (https://docs.pytest.org/en/stable/goodpractices.html#test-discovery)
- Começa a procurar a partir do testpaths (se configurados) ou do diretorio atual
- Analisa os diretorios recursivamente
- Nesses diretórios, procure por arquivos test_*.py or *_test.py
- From those files, collect test items:
  - test prefixed test functions or methods outside of class
  - test prefixed test functions or methods inside Test prefixed test classes (without an __init__ method)
- Usando a técnica de subclasse do unittest.TestCase (apesar de não ter necessidade de criar subclasses)


Layouts de teste:
- Testes fora do código da aplicação
```
setup.py
mypkg/
    __init__.py
    app.py
    view.py
tests/
    test_app.py
    test_view.py
    ...
```

- Testes como parte do código da aplicação
```
setup.py
mypkg/
    __init__.py
    app.py
    view.py
    test/
        __init__.py
        test_app.py
        test_view.py
        ...
```
 If you use one of the two recommended file system layouts above but leave away the `__init__.py` files from your directories it should just work on Python3.3 and above.

-------
## Lista de ferramentas de teste em python
https://wiki.python.org/moin/PythonTestingToolsTaxonomy

find_packages("src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"])
https://www.tutorialspoint.com/unittest_framework/unittest_framework_overview.htm

--------
As stated in https://google.github.io/styleguide/pyguide.html "There is no One Correct Way to name test methods."

Discussão sobre boas praticas para nomenclatura de testes (geral, não especificamente para python)
https://stackoverflow.com/questions/155436/unit-test-naming-best-practices

There is a python tool called unittest2pytest that can help automate parts of this conversion





https://github.com/iterative/dvc/issues/1819
https://github.com/gaphor/gaphor/issues/129   # still open
https://github.com/sgeisler/termgraph/issues/15
https://github.com/simpeg/simpeg/issues/702



Casos a considerar:
- Quando o arquivo de teste usa os dois
- Quando o arquito de teste nao importa pytest explicitamente (foge da premissa de seguir as sugestões das documentações/boas práticas)

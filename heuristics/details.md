# Unittest

[From unittest docs](https://docs.python.org/3/library/unittest.html)

_A testcase is created by subclassing unittest.TestCase._ (...) To make your own test cases you must write subclasses of TestCase or use FunctionTestCase.
- Subclasses dessas subclasses também são válidas
- [Python issubclass()](https://www.geeksforgeeks.org/python-issubclass/)

Note: Even though FunctionTestCase can be used to quickly convert an existing test base over to a unittest-based system, this approach is not recommended. Taking the time to set up proper TestCase subclasses will make future test refactorings infinitely easier.
In some cases, the existing tests may have been written using the doctest module. If so, doctest provides a DocTestSuite class that can automatically build unittest.TestSuite instances from the existing doctest-based tests.
- Desconsiderar doctest?
- E se a pessoa remover os imports do unittest, achar que migrou, mas continuar com doctest? :thinking:

_The (...) individual tests are defined with methods whose names start with the letters test. This naming convention informs the test runner about which methods represent tests._


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


# Pytest

[Da documentação](https://docs.pytest.org/en/stable/)

Primeiramente, deve-se instalar o pacote:
```sh
pip install -U pytest
```

_pytest will run all files of the form `test_*.py` or `*_test.py` in the current directory
and its subdirectories. More generally, it follows standard test discovery rules._
_Within Python modules, pytest also discovers tests using the standard unittest.TestCase subclassing technique._
https://docs.pytest.org/en/stable/goodpractices.html#test-discovery
_pytest discovers all tests following its Conventions for Python test discovery,
so it finds both test_ prefixed functions. There is no need to subclass anything,
but make sure to prefix your class with Test otherwise the class will be skipped._


_You can also gradually move away from subclassing from unittest.TestCase to plain asserts and then start to benefit from the full pytest feature set step by step._

Como é possível executar:
```sh
pytest _test_folder
```


-------
## Lista de ferramentas de teste em python
https://wiki.python.org/moin/PythonTestingToolsTaxonomy

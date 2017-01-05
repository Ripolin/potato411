# Tests management

## Install dependencies

```pip2 install -U -r requirements.txt```

## How to run

Before run tests, create inside the test dir a file named `test.cfg` by copying the file `example.cfg`. Fill the properties `username` and `password` with your T411 account information.

Now you're able to run unit tests by launching the command : ```$python -m pytest test/test.py t411 --pep8 --cov t411 --cov-report term-missing```

You should see something like this :
```console
============================= test session starts =============================
platform win32 -- Python 2.7.12, pytest-3.0.5, py-1.4.32, pluggy-0.4.0 -- C:\Python27\python.exe
cachedir: .cache
rootdir: F:\workspace\potato411, inifile:
plugins: cov-2.4.0, pep8-1.0.6
collecting ... collected 9 items

test/test.py PASSED
test/test.py::TestPotato411::test_loginKO PASSED
test/test.py::TestPotato411::test_login PASSED
test/test.py::TestPotato411::test_searchMovie PASSED
test/test.py::TestPotato411::test_searchMovieWithAccent PASSED
test/test.py::TestPotato411::test_searchAnim PASSED
test/test.py::TestPotato411::test_quality PASSED
test/test.py::TestPotato411::test_download PASSED
test/test.py::TestPotato411::test_error PASSED

---------- coverage: platform win32, python 2.7.12-final-0 -----------
Name           Stmts   Miss  Cover   Missing
--------------------------------------------
t411\t411.py      83     10    88%   52-53, 103-107, 112, 152-156


========================== 9 passed in 4.60 seconds ===========================
```

Cfg files are snippets of the CouchPotato configuration file `settings.conf`. Depending your execution environment (proxies, etc...), you can customize them if necessary to run unit tests.

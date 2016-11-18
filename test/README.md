# Tests management

## Install dependencies

```pip2 install -U -r requirements.txt```

## How to run

Before run tests, create inside the test dir a file named `test.cfg` by copying the file `example.cfg`. Fill the properties `username` and `password` with your T411 account information.

Now you're able to run unit tests by launching the command : ```$python -m pytest test/test.py --pep8 --cov t411/t411.py --cov-report term-missing```

You should see something like this :
```bash
============================= test session starts ==============================
platform linux2 -- Python 2.7.9 -- py-1.4.26 -- pytest-2.6.4
plugins: cache, pep8, cov
collected 9 items

test/test.py .........

---------- coverage: platform linux2, python 2.7.9-final-0 -----------
Name           Stmts   Miss  Cover   Missing
--------------------------------------------
t411/t411.py     102      4    96%   93-94, 188-189


=========================== 9 passed in 2.55 seconds ===========================
```

Cfg files are snippets of the CouchPotato configuration file `settings.conf`. Depending your execution environment (proxies, etc...), you can customize them if necessary to run unit tests.

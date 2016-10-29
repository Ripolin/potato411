# Tests management

## Install dependencies

```pip2 install -U -r requirements.txt```

## How to run

Before run tests, create inside the test dir a file named `test.cfg` by copying the file `example.cfg`. Fill the properties `username` and `password` with your T411 account informations.

Now you're able to run unit tests by launching the command : ```$python -m pytest test/test.py t411/main.py --cov t411/main.py --cov-report term-missing```

```bash
You should see something like this :
================================ test session starts ================================
platform linux2 -- Python 2.7.9, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
plugins: cov-2.4.0
collected 5 items

test/test.py .....

---------- coverage: platform linux2, python 2.7.9-final-0 -----------
Name           Stmts   Miss  Cover   Missing
--------------------------------------------
t411/main.py     100      9    91%   47-48, 81-82, 108-111, 162-163


============================== 5 passed in 10.41 seconds =============================
```

Cfg files are snippets of the CouchPotato configuration file `config.ini`. Depending your execution environment (proxies, etc...), you can customize them if necessary to run unit tests.

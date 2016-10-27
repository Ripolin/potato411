# Tests management

## How to run

Before run tests, create inside the test dir a file named `test.cfg` by copying the file `example.cfg`. Fill the properties `username` and `password` with your T411 account informations.

Now you're able to run unit tests by launching the command : ```$python test.py```

You should see something like this :

```bash
test_login (__main__.TestPotato411) ... Starting new HTTPS connection (1): api.t411.ch
"POST /auth HTTP/1.1" 200 None
ok
test_loginKO (__main__.TestPotato411) ... Starting new HTTPS connection (1): api.t411.ch
"POST /auth HTTP/1.1" 200 None
[                     main] T411 return code 107: Wrong password
ok
test_searchMovie (__main__.TestPotato411) ... [                     main] the bourne identity 1080p
Starting new HTTPS connection (1): api.t411.ch
"GET /torrents/search/the%20bourne%20identity%201080p?offset=0&limit=50&cid=631 HTTP/1.1" 200 None
[                     main] 4660818|true hd the bourne identity 2002 bluray 1080p vc1 dts hdma chdbits
[                     main] 4826118|the bourne identity 2002 truefrench 720p bluray x264 autopsiehd
[                     main] 5174086|the bourne 1 identity 2002 multi vf2 1080p hdlight x264 tonyk la memoire dans la peau
ok
test_searchMovieWithAccent (__main__.TestPotato411) ... [                     main] les delices de tokyo 1080p
Starting new HTTPS connection (1): api.t411.ch
"GET /torrents/search/les%20delices%20de%20tokyo%201080p?offset=0&limit=50&cid=631 HTTP/1.1" 200 None
[                     main] 5532899|les delices de tokyo 2015 vostfr 1080p bluray x264 dts wiki
ok

----------------------------------------------------------------------
Ran 4 tests in 1.473s

OK
```

Cfg files are snippets of the CouchPotato configuration file `config.ini`. Depending your execution environment (proxies, etc...), you can customize them if necessary to run unit tests.

# coding: utf8
from os.path import dirname
import logging
import os
import pytest
import requests
import sys
import time

from cache import BaseCache
from couchpotato.core.settings import Settings
from couchpotato.core.plugins.quality import QualityPlugin
from couchpotato.environment import Env
from t411 import T411, T411Error

base_path = dirname(os.path.abspath(__file__))
plug = QualityPlugin()
qualities = plug.qualities
handler = logging.StreamHandler(sys.stdout)


class NoCache(BaseCache):
    def get(self, key):
        pass


class TestPotato411:

    def setUp(self, conf='/test.cfg'):
        settings = Settings()
        settings.setFile(base_path+conf)
        Env.set('settings', settings)
        Env.set('http_opener', requests.Session())
        Env.set('cache', NoCache())
        t411 = T411()
        t411.log.logger.setLevel('DEBUG')
        t411.log.logger.addHandler(handler)
        return t411

    def test_loginKO(self):
        t411 = self.setUp(conf='/wrong.cfg')
        assert not t411.login()

    def test_login(self):
        t411 = self.setUp()
        isLogged = t411.login()
        assert isLogged
        isLogged = t411.login()
        assert isLogged

    def test_loginCheck(self):
        t411 = self.setUp()
        t411.last_login_check = time.time()-7200
        isLogged = t411.login()
        assert isLogged
        isLogged = t411.login()
        assert isLogged

    def test_searchMovie(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt0258463',
            'type': 'movie',
            'category': {'required': ''},
            'info': {'year': 2002}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'the bourne identity', media, qualities[2],
                                results)
            assert len(results) > 0

    def test_searchMovieWithAccent(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt2948356',
            'type': 'movie',
            'category': {'required': ''},
            'info': {'year': 2015}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'les délices de tokyo', media, qualities[2],
                                results)
            assert len(results) > 0

    def test_searchMoviePagination(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt0258463',
            'type': 'movie',
            'category': {'required': ''},
            'info': {'year': 2009}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'avatar', media, qualities[2], results)
            ids = list()
            for result in results:
                if result['id'] not in ids:
                    ids.append(result['id'])
            assert len(results) == len(ids)  # No duplication
            assert len(results) > t411.limit

    def test_searchAnim(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt2948356',
            'type': 'movie',
            'category': {'required': ''},
            'info': {'year': 2016}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'zootopia', media, qualities[2], results)
            assert len(results) > 0

    def test_getMoreInfo(self):
        t411 = self.setUp()
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            nzb = {
                'id': 5229736,
                'name': 'Jin-Roh, la Brigade des Loups 1080p MULTI x264 -'
                        ' Kayneth',
                'year': '1999'
            }
            t411.getMoreInfo(nzb)
            assert nzb['description'] is not None

    def test_download(self):
        t411 = self.setUp()
        data = t411.loginDownload(t411.urls['url']+'5549739')
        assert len(data) > 0

    def test_error(self):
        t411 = self.setUp()
        data = {
            'code': 101,
            'error': 'User not found'
        }
        with pytest.raises(T411Error):
            t411.checkError(data)

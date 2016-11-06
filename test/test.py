# coding: utf8
from os.path import dirname
import logging
import os
import sys

from couchpotato.core.settings import Settings
from couchpotato.core.plugins.quality import QualityPlugin
from couchpotato.environment import Env
from t411 import T411

base_path = dirname(os.path.abspath(__file__))
plug = QualityPlugin()
qualities = plug.qualities
handler = logging.StreamHandler(sys.stdout)


class TestPotato411:

    def setUp(self, conf='/test.cfg'):
        settings = Settings()
        settings.setFile(base_path+conf)
        Env.set('settings', settings)
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

    def test_searchMovie(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt0258463',
            'type': 'movie',
            'category': {'required': ''}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'the bourne identity', media,
                                qualities[2], results)
            assert len(results) > 0

    def test_searchMovieWithAccent(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt2948356',
            'type': 'movie',
            'category': {'required': ''}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'les délices de tokyo', media,
                                qualities[2], results)
            assert len(results) > 0

    def test_searchAnim(self):
        t411 = self.setUp()
        results = []
        media = {
            'identifier': 'tt',
            'type': 'movie',
            'category': {'required': ''}
        }
        isLogged = t411.login()
        assert isLogged
        if isLogged:
            t411._searchOnTitle(u'zootopia', media,
                                qualities[2], results)
            assert len(results) > 0

    def test_authproxy(self):
        t411 = self.setUp('/authproxy.cfg')
        proxies = t411.getProxySetting()
        assert proxies['http'] == 'http://jdoe:supersecure@mytestproxy.com'

    def test_proxy(self):
        t411 = self.setUp('/proxy.cfg')
        proxies = t411.getProxySetting()
        assert proxies['http'] == 'http://mytestproxy.com'

    def test_quality(self):
        t411 = self.setUp()
        snippet = t411.formatQuality(qualities[5])
        assert snippet == 'dvdr|br2dvd|(dvd&r)'

    def test_download(self):
        t411 = self.setUp()
        data = t411.loginDownload(t411.urls['url']+'5549739')
        assert len(data) > 0

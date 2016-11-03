# coding: utf8
from os.path import dirname
import logging
import os
import sys

# Root path
base_path = dirname(os.path.abspath(__file__))

# Insert local directories into path
sys.path.insert(0, os.path.join(base_path, '../couchpotato/libs'))
sys.path.insert(1, os.path.join(base_path, '../couchpotato'))
sys.path.insert(2, os.path.join(base_path, '../t411'))

from couchpotato.core.settings import Settings  # nopep8
from couchpotato.core.plugins.quality import QualityPlugin  # nopep8
from couchpotato.environment import Env  # nopep8
from t411 import T411  # nopep8

plug = QualityPlugin()
qualities = plug.qualities
level = 'DEBUG'
handler = logging.StreamHandler(sys.stdout)


class TestPotato411:

    def setUp(self, conf='/test.cfg'):
        settings = Settings()
        settings.setFile(base_path+conf)
        Env.set('settings', settings)
        self.t411 = T411()
        self.t411.log.logger.setLevel(level)
        self.t411.log.logger.addHandler(handler)

    def test_login(self):
        self.setUp()
        assert self.t411.login()

    def test_loginKO(self):
        self.setUp(conf='/wrong.cfg')
        assert not self.t411.login()

    def test_searchMovie(self):
        self.setUp()
        results = []
        media = {
            'identifier': 'tt0258463',
            'type': 'movie',
            'category': {'required': ''}
        }
        self.t411._searchOnTitle(u'the bourne identity', media,
                                 qualities[2], results)
        assert len(results) > 0

    def test_searchMovieWithAccent(self):
        self.setUp()
        results = []
        media = {
            'identifier': 'tt4298958',
            'type': 'movie',
            'category': {'required': ''}
        }
        self.t411._searchOnTitle(u'les délices de tokyo', media,
                                 qualities[2], results)
        assert len(results) > 0

    def test_authproxy(self):
        self.setUp('/authproxy.cfg')
        proxies = self.t411.getProxySetting()
        assert proxies['http'] == 'http://jdoe:supersecure@mytestproxy.com'

    def test_proxy(self):
        self.setUp('/proxy.cfg')
        proxies = self.t411.getProxySetting()
        assert proxies['http'] == 'http://mytestproxy.com'

    def test_quality(self):
        self.setUp()
        snippet = self.t411.formatQuality(qualities[5])
        assert snippet == 'dvdr|br2dvd|(dvd&r)'

    def test_download(self):
        self.setUp()
        data = self.t411.loginDownload(self.t411.urls['url'], 5549739)
        assert len(data) > 0

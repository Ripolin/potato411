# coding: utf8
from couchpotato.core.helpers.encoding import simplifyString
from couchpotato.core.helpers.variable import getIdentifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
from couchpotato.environment import Env
import datetime
import json
import requests
import traceback
import urllib


class T411(TorrentProvider, MovieProvider):
    """
    Couchpotato plugin to search movies torrents using T411 APIs. More
    information about T411 APIs on https://api.t411.ch.
    """

    urlProtocol = 'https'
    basePathApi = 'api.t411.ch'
    basePathWww = 'www.t411.ch'
    tokenTTL = 90  # T411 authentication token TTL = 90 days
    tokenTimestamp = None
    headers = {}
    log = CPLog(__name__)

    def __init__(self):
        """
        Default constructor
        """
        TorrentProvider.__init__(self)
        MovieProvider.__init__(self)
        wwwLoc = self.urlProtocol+'://'+self.basePathWww
        apiLoc = self.urlProtocol+'://'+self.basePathApi
        self.urls = {
            'login': apiLoc+'/auth',
            'search': apiLoc+'/torrents/search/',
            'url': apiLoc+'/torrents/download/',
            'detail_url': wwwLoc+'/torrents/?id='
        }

    def getProxySetting(self):
        """
        Get the CouchPotato proxy setting.
        """
        result = None
        if(Env.setting('use_proxy')):
            proxy_server = Env.setting('proxy_server')
            proxy_username = Env.setting('proxy_username')
            proxy_password = Env.setting('proxy_password')
            if(proxy_server):
                if(proxy_username):
                    loc = '{0}:{1}@{2}'.format(proxy_username,
                                               proxy_password, proxy_server)
                else:
                    loc = proxy_server
                result = {
                    "http": "http://"+loc,
                    "https": "https://"+loc,
                }
            else:
                result = urllib.getproxies()
        return result

    def urlopen(self, method, url, params=None, headers=None, data=None,
                check=True):
        """
        Proxyfi request to T411. T411 API reject all requests with
        a 'User-Agent' HTTP header, it's why we don't use the
        couchpotato.core.plugins.base.py#Plugin.urlopen(...) method.
        Furthermore Plugin.urlopen(...) don't let the caller handle the HTTP
        method. We also don't use the session hide behind the
        Env.get('http_opener') function, T411 API calls are stateless.
        """
        response = method(url, params=params, headers=headers,
                          proxies=self.getProxySetting(), data=data,
                          timeout=30)
        response.raise_for_status()
        if(check):
            error = response.json().get('error')
            if(error):
                code = response.json().get('code')
                raise T411Error(code, error)
        return response

    def loginDownload(self, url='', nzb_id=''):
        """
        Override couchpotato.core.media._base.providers.base.py#YarrProvider.
        loginDownload(...) method. It log to the T411 torrents provider and
        retrieve the torrent file researched as binary data.
        """
        result = None
        try:
            if(self.login()):
                result = self.urlopen(requests.get, url+str(nzb_id),
                                      headers=self.headers,
                                      check=False).content
        except:
            self.log.error('Failed getting release from %s: %s',
                           self.getName(), traceback.format_exc())
        return result

    def getToken(self):
        """
        Get T411 HTTP authentication header.
        """
        now = datetime.datetime.now()
        if(self.tokenTimestamp is None) or ((now - self.tokenTimestamp).
                                            days >= self.tokenTTL):
            login = {
                'username': self.conf('username'),
                'password': self.conf('password')
            }
            auth = self.urlopen(requests.post, self.urls.get('login'),
                                data=login)
            data = auth.json()
            self.tokenTimestamp = now
            self.token = data['token']
        return self.token

    def formatQuality(self, quality):
        """
        Generate a snippet of a T411 searching request by adding the current
        quality term and its alternatives. For more informations see
        http://www.t411.ch/faq/#300.
        """
        result = [quality.get('identifier')]
        for alt in quality.get('alternative'):
            if(isinstance(alt, basestring)):
                result.append(alt)
            else:
                result.append('({0})'.format('&'.join(alt)))
        return '|'.join(result)

    def login(self):
        """
        Override couchpotato.core.media._base.providers.base.py#YarrProvider.
        login(...) method. Log to the torrents provider and store the HTTP
        header token.
        """
        result = False
        try:
            token = self.getToken()
            if(token):
                self.headers['Authorization'] = token
                result = True
        except T411Error as e:
            self.log.error('T411 return code {0}: {1}'.format(e.code,
                                                              e.message))
        return result

    def _searchOnTitle(self, title, media, quality, results):
        """
        Do the job ;P. See couchpotato.core.media._base.providers.base.py#
        YarrProvider.search(...) method for more informations.
        """
        try:
            params = {
                'cid': 631,  # Movie category
                'offset': 0,
                'limit': 50  # We only select the 50 firsts results
            }
            query = '{0} {1}'.format(simplifyString(title),
                                     self.formatQuality(quality))
            self.log.debug(query)
            url = self.urls['search']+urllib.quote(query)
            search = self.urlopen(requests.get, url, params=params,
                                  headers=self.headers)
            data = search.json()
            now = datetime.datetime.now()
            for torrent in data['torrents']:
                added = datetime.datetime.strptime(torrent['added'],
                                                   '%Y-%m-%d %H:%M:%S')
                # Convert size from byte to kilobyte
                size = int(torrent['size'])/1024
                result = {
                    'id': int(torrent['id']),
                    'name': torrent['name'],
                    'seeders': int(torrent['seeders']),
                    'leechers': int(torrent['leechers']),
                    'size': self.parseSize(str(size)+'kb'),
                    'age': (now - added).days,
                    'url': self.urls['url'],
                    'detail_url': self.urls['detail_url']+torrent['id'],
                    'verified': bool(int(torrent['isVerified']))
                }
                self.log.debug('{0}|{1}'.format(result.get('id'),
                               simplifyString(result.get('name'))))
                results.append(result)
        except:
            self.log.error('Failed searching release from %s: %s',
                           self.getName(), traceback.format_exc())


class T411Error(Exception):
    """
    Representation of a T411 error.
    """

    def __init__(self, code, message):
        """
        Default constructor
        """
        Exception.__init__(self)
        self.code = code
        self.message = message

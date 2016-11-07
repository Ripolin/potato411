# coding: utf8
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
from datetime import datetime
import traceback


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
    http_time_between_calls = 0
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
            'search': apiLoc+'/torrents/search/{0} {1}?{2}',
            'url': apiLoc+'/torrents/download/',
            'detail_url': wwwLoc+'/torrents/?id='
        }
        self.headers = {
            'Authorization': None
        }

    def loginDownload(self, url='', nzb_id=''):
        """
        Override couchpotato.core.media._base.providers.base.py#YarrProvider.
        loginDownload(...) method. It appends T411 HTTP authentication header.
        """
        result = None
        try:
            if self.login():
                result = self.urlopen(url, headers=self.headers)
        except:
            self.log.error('Failed getting release from {0}: {1}'.
                            format(self.getName(), traceback.format_exc()))
        return result

    def formatQuality(self, quality):
        """
        Generate a snippet of a T411 searching request by adding the current
        quality term and its alternatives. For more informations see
        http://www.t411.ch/faq/#300.
        """
        result = [quality.get('identifier')]
        for alt in quality.get('alternative'):
            if isinstance(alt, basestring):
                result.append(alt)
            else:
                result.append('({0})'.format('&'.join(alt)))
        return '|'.join(result)

    def login(self):
        """
        Override couchpotato.core.media._base.providers.base.py#YarrProvider.
        login(...) method. Log to T411 torrents provider and store the HTTP
        authentication header token.
        """
        result = True
        now = datetime.now()
        if (self.tokenTimestamp is None) or ((now - self.tokenTimestamp).
                                             days >= self.tokenTTL):
            kwargs = {
                'data': {
                    'username': self.conf('username'),
                    'password': self.conf('password')
                }
            }
            try:
                data = self.getJsonData(self.urls.get('login'), **kwargs)
                self.headers['Authorization'] = data['token']
                self.tokenTimestamp = now
            except:
                if data and ('error' in data):
                    self.log.error('T411 error code {0}: {1}'.
                                   format(data['code'], data['error']))
                else:
                    self.log.error('Failed to login {0}: {1}'.
                                   format(self.getName(),
                                          traceback.format_exc()))
                self.login_failures += 1
                if self.login_failures >= 3:
                    self.disableAccount()
                result = False
        return result

    def _searchOnTitle(self, title, media, quality, results):
        """
        Do the job ;P. See couchpotato.core.media._base.providers.base.py#
        YarrProvider.search(...) method for more informations.
        """
        try:
            params = {
                'cid': 210,  # Movie/Video category
                'offset': 0,
                'limit': 50  # We only select the 50 firsts results
            }
            kwargs = {
                'headers': self.headers
            }
            url = self.urls['search'].format(simplifyString(title),
                                             self.formatQuality(quality),
                                             tryUrlencode(params))
            data = self.getJsonData(url, **kwargs)
            now = datetime.now()
            for torrent in data['torrents']:
                added = datetime.strptime(torrent['added'],
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
                    'url': self.urls['url']+torrent['id'],
                    'detail_url': self.urls['detail_url']+torrent['id'],
                    'verified': bool(int(torrent['isVerified']))
                }
                self.log.debug('{0}|{1}'.format(result.get('id'),
                               simplifyString(result.get('name'))))
                results.append(result)
        except:
            self.log.error('Failed searching release from {0}: {1}'.
                            format(self.getName(), traceback.format_exc()))

# coding: utf8
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
from datetime import datetime
import json
import traceback


class T411(TorrentProvider, MovieProvider):
    """
    Couchpotato plugin to search movies torrents using T411 APIs. More
    information about T411 APIs on https://api.t411.li.
    """

    url_scheme = 'https'
    url_netloc_api = 'api.t411.li'
    url_netloc_www = 'www.t411.li'
    token_ttl = 90  # T411 authentication token TTL = 90 days
    token_timestamp = None
    login_fail_msg = 'Wrong password'
    http_time_between_calls = 0
    log = CPLog(__name__)

    def __init__(self):
        """
        Default constructor
        """
        TorrentProvider.__init__(self)
        MovieProvider.__init__(self)
        path_www = self.url_scheme+'://'+self.url_netloc_www
        path_api = self.url_scheme+'://'+self.url_netloc_api
        self.urls = {
            'login': path_api+'/auth',
            'login_check': path_api,  # Useless entry to validate login API
            'search': path_api+'/torrents/search/{0} {1}?{2}',
            'url': path_api+'/torrents/download/',
            'detail_url': path_www+'/torrents/?id='
        }
        self.headers = {
            'Authorization': None
        }

    def loginDownload(self, url='', nzb_id=''):
        """
        It appends a T411 HTTP authentication header to the download request.
        Override the YarrProvider.loginDownload method.

        .. seealso:: YarrProvider.loginDownload
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
        quality term and its alternatives. For more information see
        http://www.t411.li/faq/#300.
        """
        result = [quality.get('identifier')]
        for alt in quality.get('alternative'):
            if isinstance(alt, basestring):
                result.append(alt)
            else:
                result.append('({0})'.format('&'.join(alt)))
        return '|'.join(result)

    def checkError(self, data):
        """
        Check if T411 send an error.
        """
        if data and ('error' in data):
            e = T411Error(data['code'], data['error'])
            self.log.error('T411 return code {0}: {1}'.format(e.code,
                                                              e.message))
            raise e

    def getLoginParams(self):
        """
        Return T411 login parameters.

        .. seealso:: YarrProvider.getLoginParams
        """
        return {
            'username': self.conf('username'),
            'password': self.conf('password')
        }

    def loginSuccess(self, output):
        """
        Log to T411 torrents provider and store the HTTP authentication
        header token.

        .. seealso:: YarrProvider.loginSuccess
        """
        try:
            data = json.loads(output)
            self.checkError(data)
            self.headers['Authorization'] = data['token']
            self.token_timestamp = datetime.now()
        except:
            raise
        return True

    def loginCheckSuccess(self, output):
        """
        Only check the validity of the user token. Output parameter is
        useless, just here to validate the login API compliance.

        .. seealso:: YarrProvider.loginCheckSuccess
        """
        result = True
        now = datetime.now()
        if (self.token_timestamp is None) or ((now - self.token_timestamp).
                                              days >= self.token_ttl):
            result = False
        return result

    def _searchOnTitle(self, title, media, quality, results):
        """
        Do a T411 search based on possible titles.

        .. seealso:: YarrProvider.search
        """
        try:
            params = {
                'cid': 210,  # Movie/Video category
                'offset': 0,
                'limit': 50  # We only select the 50 firsts results
            }
            url = self.urls['search'].format(simplifyString(title),
                                             self.formatQuality(quality),
                                             tryUrlencode(params))
            data = self.getJsonData(url, headers=self.headers)
            self.checkError(data)
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
                    'size': self.parseSize(str(size)+self.size_kb[0]),
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
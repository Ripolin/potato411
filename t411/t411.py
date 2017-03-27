# coding: utf8
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.helpers.variable import getImdb
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
    domain_name = 't411.ai'
    token_ttl = 90  # T411 authentication token TTL = 90 days
    token_timestamp = None
    limit = 200
    login_fail_msg = 'Wrong password'  # Used by YarrProvider.login()
    http_time_between_calls = 0
    log = CPLog(__name__)

    def __init__(self):
        """
        Default constructor
        """
        TorrentProvider.__init__(self)
        MovieProvider.__init__(self)
        path_www = self.url_scheme+'://www.'+self.domain_name
        path_api = self.url_scheme+'://api.'+self.domain_name
        self.urls = {
            'login': path_api+'/auth',  # Used by YarrProvider.login()
            'login_check': path_api,  # Used by YarrProvider.login()
            'search': path_api+'/torrents/search/{0}?{1}',
            'url': path_api+'/torrents/download/',
            'detail': path_api+'/torrents/details/{0}',
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

    def checkError(self, data):
        """
        Check if T411 send an error.
        """
        if data and ('error' in data):
            e = T411Error(data['code'], data['error'])
            self.log.error('T411 return code {0}: {1}'.format(e.code,
                                                              e.message))
            # Error 202 = Invalid token
            if e.code == 202:
                self.headers['Authorization'] = None
                self.token_timestamp = None
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

    def getMoreInfo(self, nzb):
        """
        Get details about a T411 torrent.

        .. seealso:: MovieSearcher.correctRelease
        """
        url = self.urls['detail'].format(nzb['id'])
        data = self.getJsonData(url, headers=self.headers)
        self.checkError(data)
        nzb['description'] = data['description']

    def extraCheck(self, nzb):
        """
        Exclusion when movie's description contains more than one IMDB
        reference to prevent a movie bundle downloading. CouchPotato
        is not able to extract a specific movie from an archive.

        .. seealso:: MovieSearcher.correctRelease
        """
        result = True
        ids = getImdb(nzb.get('description', ''), multiple=True)
        if len(ids) not in [0, 1]:
            self.log.info('Too much IMDB movies: {0}'.format(', '.join(ids)))
            result = False
        return result

    def _searchOnTitle(self, title, media, quality, results, offset=0):
        """
        Do a T411 search based on possible titles. This function doesn't check
        the quality because CouchPotato do the job when parsing results.
        Furthermore the URL must stay generic to use native CouchPotato
        caching feature.

        .. seealso:: YarrProvider.search
        """
        try:
            params = {
                'cid': 210,  # Movie/Video category
                'offset': offset,
                'limit': self.limit
            }
            url = self.urls['search'].format(simplifyString(title),
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
                    'verified': bool(int(torrent['isVerified'])),
                    'get_more_info': self.getMoreInfo,
                    'extra_check': self.extraCheck
                }
                self.log.debug('{0}|{1}'.format(result.get('id'),
                               simplifyString(result.get('name'))))
                results.append(result)
            # Get next page if we don't have all results
            if int(data['total']) > len(data['torrents'])+offset:
                self._searchOnTitle(title, media, quality, results,
                                    offset+self.limit)
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
        self.code = int(code)
        self.message = message

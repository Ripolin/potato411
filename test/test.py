# coding: utf8
from os.path import dirname
import ConfigParser
import logging
import os
import sys

# Root path
base_path = dirname(os.path.abspath(__file__))

# Insert local directories into path
sys.path.insert(0, os.path.join(base_path, '../lib/libs'))
sys.path.insert(1, os.path.join(base_path, '../lib'))
sys.path.insert(2, os.path.join(base_path, '../t411'))

from couchpotato.core.media._base.providers.base import ResultList
from couchpotato.core.settings import Settings
from couchpotato.environment import Env
from main import T411

settings = Settings()
settings.setFile(base_path+'/test.cfg')
Env.set('settings', settings)
handler = logging.StreamHandler(sys.stdout)

t411 = T411()
t411.log.logger.setLevel('DEBUG')
t411.log.logger.addHandler(handler)

qualities = [
    {'identifier': '2160p', 'hd': True, 'allow_3d': True, 'size': (10000, 650000), 'median_size': 20000, 'label': '2160p', 'width': 3840, 'height': 2160, 'alternative': [], 'allow': [], 'ext':['mkv'], 'tags': ['x264', 'h264', '2160']},
    {'identifier': 'bd50', 'hd': True, 'allow_3d': True, 'size': (20000, 60000), 'median_size': 40000, 'label': 'BR-Disk', 'alternative': ['bd25', ('br', 'disk')], 'allow': ['1080p'], 'ext':['iso', 'img'], 'tags': ['bdmv', 'certificate', ('complete', 'bluray'), 'avc', 'mvc']},
    {'identifier': '1080p', 'hd': True, 'allow_3d': True, 'size': (4000, 20000), 'median_size': 10000, 'label': '1080p', 'width': 1920, 'height': 1080, 'alternative': [], 'allow': [], 'ext':['mkv', 'm2ts', 'ts'], 'tags': ['m2ts', 'x264', 'h264', '1080']},
    {'identifier': '720p', 'hd': True, 'allow_3d': True, 'size': (3000, 10000), 'median_size': 5500, 'label': '720p', 'width': 1280, 'height': 720, 'alternative': [], 'allow': [], 'ext':['mkv', 'ts'], 'tags': ['x264', 'h264', '720']},
    {'identifier': 'brrip', 'hd': True, 'allow_3d': True, 'size': (700, 7000), 'median_size': 2000, 'label': 'BR-Rip', 'alternative': ['bdrip', ('br', 'rip'), 'hdtv', 'hdrip'], 'allow': ['720p', '1080p'], 'ext':['mp4', 'avi'], 'tags': ['webdl', ('web', 'dl')]},
    {'identifier': 'dvdr', 'size': (3000, 10000), 'median_size': 4500, 'label': 'DVD-R', 'alternative': ['br2dvd', ('dvd', 'r')], 'allow': [], 'ext':['iso', 'img', 'vob'], 'tags': ['pal', 'ntsc', 'video_ts', 'audio_ts', ('dvd', 'r'), 'dvd9']},
    {'identifier': 'dvdrip', 'size': (600, 2400), 'median_size': 1500, 'label': 'DVD-Rip', 'width': 720, 'alternative': [('dvd', 'rip')], 'allow': [], 'ext':['avi'], 'tags': [('dvd', 'rip'), ('dvd', 'xvid'), ('dvd', 'divx')]},
    {'identifier': 'scr', 'size': (600, 1600), 'median_size': 700, 'label': 'Screener', 'alternative': ['screener', 'dvdscr', 'ppvrip', 'dvdscreener', 'hdscr', 'webrip', ('web', 'rip')], 'allow': ['dvdr', 'dvdrip', '720p', '1080p'], 'ext':[], 'tags': []},
    {'identifier': 'r5', 'size': (600, 1000), 'median_size': 700, 'label': 'R5', 'alternative': ['r6'], 'allow': ['dvdr', '720p', '1080p'], 'ext':[]},
    {'identifier': 'tc', 'size': (600, 1000), 'median_size': 700, 'label': 'TeleCine', 'alternative': ['telecine'], 'allow': ['720p', '1080p'], 'ext':[]},
    {'identifier': 'ts', 'size': (600, 1000), 'median_size': 700, 'label': 'TeleSync', 'alternative': ['telesync', 'hdts'], 'allow': ['720p', '1080p'], 'ext':[]},
    {'identifier': 'cam', 'size': (600, 1000), 'median_size': 700, 'label': 'Cam', 'alternative': ['camrip', 'hdcam'], 'allow': ['720p', '1080p'], 'ext':[]}
]

if(t411.login()):
    results = ResultList(t411, {'identifier': 'tt0110912', 'type': 'movie'}, qualities[2], imdb_results = False)
    t411._searchOnTitle(u'pulp fiction', {'identifier': 'tt0110912', 'type': 'movie'}, qualities[2], results)
    results = ResultList(t411, {'identifier': 'tt1922645', 'type': 'movie'}, qualities[2], imdb_results = False)
    t411._searchOnTitle(u'la fée', {'identifier': 'tt1922645', 'type': 'movie'}, qualities[2], results)
    results = ResultList(t411, {'identifier': 'tt4513674', 'type': 'movie'}, qualities[2], imdb_results = False)
    t411._searchOnTitle(u'café society', {'identifier': 'tt4513674', 'type': 'movie'}, qualities[2], results)
    results = ResultList(t411, {'identifier': 'tt1599348', 'type': 'movie'}, qualities[2], imdb_results = False)
    t411._searchOnTitle(u'safe house', {'identifier': 'tt1599348', 'type': 'movie'}, qualities[2], results)
    results = ResultList(t411, {'identifier': 'tt4298958', 'type': 'movie'}, qualities[5], imdb_results = False)
    t411._searchOnTitle(u'les délices de tokyo', {'identifier': 'tt4298958', 'type': 'movie', 'category': {'required': ''}}, qualities[5], results)

# Test wrong authentication
settings.setFile(base_path+'/wrong.cfg')
Env.set('settings', settings)
t411 = T411()
t411.log.logger.setLevel('DEBUG')
t411.log.logger.addHandler(handler)
t411.login()

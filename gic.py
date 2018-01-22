# -*- coding: utf-8 -*-
import logging
import os
import sys
import threading
import time
from importlib import import_module

from icrawler import Downloader, Feeder, Parser
from icrawler import storage as storage_package
from icrawler.storage import BaseStorage
from icrawler.utils import ProxyPool, Session, Signal

import json
from icrawler import ImageDownloader
from icrawler.builtin import GoogleImageCrawler
from six.moves.urllib.parse import urlparse


keyword='sunny'

class MetadataDownloader(ImageDownloader):
    _filename = ''
    meta_filename = 'metadata.txt'
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    keyword = ''

    def get_filename(self, task, default_ext):
        _filename = super(MetadataDownloader, self).get_filename(
            task, default_ext)
        self._filename = 'g_' + _filename
        return self._filename

    def process_meta(self, task):
      storeDir = self.storage.root_dir
      out = task
      out['path'] = storeDir + '/' + self._filename
      out['keyword'] = self.keyword
      _filedir = os.path.join(self.fileDir, '{0}/{1}'.format(storeDir, self.meta_filename))
      fo = open(_filedir, 'w')
      line = json.dumps(out) + '\n'
      fo.write(line)

    def set_keyword(self, keyword):
      self.keyword = keyword

_MetadataDownloader = MetadataDownloader
_MetadataDownloader.set_keyword(_MetadataDownloader, keyword)
google_crawler = GoogleImageCrawler(downloader_cls=_MetadataDownloader,
                                    parser_threads=4, downloader_threads=4,
                                    storage={'root_dir': 'image'})
google_crawler.crawl(keyword=keyword, max_num=10,
                     date_min=None, date_max=None,
                     min_size=(200,200), max_size=None)
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


class MetadataDownloader(ImageDownloader):
    _filename = ''
    meta_filename = ''
    fileDir = ''
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
      fo = open(_filedir, 'a')
      line = json.dumps(out) + '\n'
      fo.write(line)
      fo.close()

    def set_keyword(self, keyword):
      self.keyword = keyword


def gic(keyword='sun', thread=5, max_num=10, minsize=(200,200), data_dir='image'):
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    meta_filename = 'metadata.txt'
    # new MetadataDownloader
    _MetadataDownloader = MetadataDownloader
    _MetadataDownloader.set_keyword(_MetadataDownloader, keyword)
    _MetadataDownloader.fileDir = fileDir
    _MetadataDownloader.meta_filename = meta_filename
    # init metafile
    _filedir = os.path.join(fileDir, '{0}/{1}'.format(data_dir, meta_filename))
    fo = open(_filedir, 'w')
    fo.write('')
    fo.close()

    google_crawler = GoogleImageCrawler(downloader_cls=_MetadataDownloader, feeder_threads=1,
                                      parser_threads=1, downloader_threads=thread*2,
                                      storage={'root_dir': data_dir})
    # usage_rights
        # f: non-commercial reuse
        # fm: non-commercial reuse with modification
        # fc: reuse
        # fmc: reuse with modification
    # img_type
        #photo
        # face
        # clipart: clip art
        # lineart: line drawing
        # animated
    # img_color
        # color: full color
        # blackandwhite: black and white
        # transparent: transparent
        # red, orange, yellow, green, teal, blue, purple, pink, white, gray, black, brown
    google_crawler.crawl(keyword=keyword, max_num=max_num*10,
                      date_min=None, date_max=None,
                      min_size=(512,512), max_size=(1920,1920),
                      usage_rights='fc', img_type=None,
                      img_color=None)

if __name__ == "__main__":
    '''
    Usage:

    '''
    # keyword=['street', 'man', 'woman', 'cat']
    keyword='street'
    gic(keyword=keyword)

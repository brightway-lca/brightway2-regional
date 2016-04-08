# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .intersection import intersections
from bw2data import config
import requests


class PandarusRemote(object):
    """Interaction with `pandarus_remote <>`__ web service.

    Default URL is `pandarus.brightwaylca.org`."""

    def __init__(self, url=None):
        self.url = url or "https://pandarus.brightwaylca.org"
        if self.url[-1] == "/":
            self.url = self.url[:-1]

    def catalog(self):
        return requests.get(self.url + "/catalog").json()


remote = PandarusRemote()

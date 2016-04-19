# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data import projects
from . import (
    geocollections,
    Intersection,
    topocollections,
)
from .utils import hash_collection
import os
import requests
import time
import wrapt


class RemoteError(Exception):
    """Can't reach pandarus-remote web service"""
    pass


class NotYetCalculated(Exception):
    """Resource hasn't been calculated yet"""
    pass


class PendingJob(object):
    """A calculation job enqueued on a remote server"""
    def __init__(self, url):
        self.url = url

    @property
    def status(self):
        return requests.get(url).content

    def poll(self, interval=10):
        while True:
            if self.status not in {'failed', 'finished'}:
                time.sleep(interval)
            else:
                break
        print("Job ended with status {}".format(self.status))


@wrapt.decorator
def check_alive(wrapped, instance, args, kwargs):
    if not instance.alive:
        raise RemoteError("Can't reach {}".format(instance.url))
    return wrapped(*args, **kwargs)


class PandarusRemote(object):
    """Interaction with `pandarus_remote <https://bitbucket.org/cmutel/pandarus_remote>`__ web service.

    Default URL is `https://pandarus.brightwaylca.org`."""

    def __init__(self, url=None):
        self.url = url or "https://pandarus.brightwaylca.org"
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.download_dirpath = projects.request_directory("regional")

    @property
    def alive(self):
        return requests.get(self.url).status_code == 200

    @check_alive
    def catalog(self):
        return requests.get(self.url + "/catalog").json()

    @check_alive
    def status(self, url):
        return requests.get(self.url + url).content

    @check_alive
    def intersection(self, collection_one, collection_two):
        first = hash_collection(collection_one)
        if not first:
            raise ValueError("Can't find collection {}".format(collection_one))
        second = hash_collection(collection_two)
        if not second:
            raise ValueError("Can't find collection {}".format(collection_two))

        resp = requests.post(
            self.url + "/intersection",
            data={'first': first, 'second': second},
            stream=True
        )
        if resp.status_code == 404:
            raise NotYetCalculated("Not yet calculated; Run `.calculate_intersection` first.")
        elif resp.status_code != 200:
            raise ValueError("Server an error code: {}".format(resp.status_code))

        assert 'Content-Disposition' in resp.headers
        filepath = os.path.join(
            self.download_dirpath,
            resp.headers['Content-Disposition'].replace('attachment; filename=', '')
        )
        chunk = 128 * 1024
        with open(filepath, "wb") as f:
            while True:
                segment = resp.raw.read(chunk)
                if not segment:
                    break
                f.write(segment)

        # Create Intersection
        return filepath


remote = PandarusRemote()


# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data import projects
from . import (
    geocollections,
    intersections,
    topocollections,
)
from .pandarus import (
    import_from_pandarus,
    import_xt_from_rasterstats,
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


class AlreadyExists(Exception):
    """Resource has already been calculated"""
    pass


class PendingJob(object):
    """A calculation job enqueued on a remote server"""
    def __init__(self, url):
        self.url = url

    @property
    def status(self):
        response = requests.get(self.url)
        if response.status_code != 404:
            return response.text
        else:
            return "forgotten"

    def poll(self, interval=10):
        try:
            while True:
                if self.status not in {'failed', 'finished', 'forgotten'}:
                    time.sleep(interval)
                else:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            print("\nJob ended with status '{}'".format(self.status))


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

    @property
    def alive(self):
        return requests.get(self.url).status_code == 200

    def _download_file(self, resp):
        assert 'Content-Disposition' in resp.headers
        download_dirpath = projects.request_directory("regional")

        filepath = os.path.join(
            download_dirpath,
            resp.headers['Content-Disposition'].replace('attachment; filename=', '')
        )
        chunk = 128 * 1024
        with open(filepath, "wb") as f:
            while True:
                segment = resp.raw.read(chunk)
                if not segment:
                    break
                f.write(segment)
        return filepath

    @check_alive
    def catalog(self):
        return requests.get(self.url + "/catalog").json()

    @check_alive
    def status(self, url):
        return requests.get(self.url + url).text

    @check_alive
    def upload(self, collection):
        if collection in topocollections:
            metadata = topocollections[collection]
        elif collection in geocollections:
            metadata = geocollections[collection]
        else:
            raise ValueError("Unknown geocollection {}".format(collection))

        assert 'filepath' in metadata, "Can't find file for this collection"

        try:
            collection_hash = metadata['sha256']
        except KeyError:
            collection_hash = hash_collection(collection)

        if collection_hash in {obj[1] for obj in self.catalog()['files']}:
            raise AlreadyExists

        url = self.url + "/upload"
        data = {
            'layer': metadata.get('layer') or '',
            'field': metadata.get('field') or '',
            'band': metadata.get('band') or '',
            'sha256': collection_hash,
            'name': os.path.basename(metadata['filepath']),
        }
        files = {'file': open(metadata['filepath'], 'rb')}
        resp = requests.post(url, data=data, files=files)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise RemoteError("{}: {}".format(resp.status_code, resp.text))

    @check_alive
    def intersection(self, collection_one, collection_two):
        if (collection_one, collection_two) in intersections:
            print("Skipping existing intersection: ({}, {})".format(
                collection_one, collection_two
            ))
            return

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
            raise ValueError("Server an error code: {}: {}".format(resp.status_code, resp.text))

        filepath = self._download_file(resp)
        return import_from_pandarus(filepath)

    @check_alive
    def intersection_as_new_geocollection(self, collection_one, collection_two, new_name):
        if new_name in geocollections:
            print("Skipping creation of existing geocollection")
            return

        first = hash_collection(collection_one)
        if not first:
            raise ValueError("Can't find collection {}".format(collection_one))
        second = hash_collection(collection_two)
        if not second:
            raise ValueError("Can't find collection {}".format(collection_two))

        resp = requests.post(
            self.url + "/intersection-file",
            data={'first': first, 'second': second},
            stream=True
        )
        if resp.status_code == 404:
            raise NotYetCalculated("Not yet calculated; Run `.calculate_intersection` first.")
        elif resp.status_code != 200:
            raise ValueError("Server an error code: {}: {}".format(resp.status_code, resp.text))

        filepath = self._download_file(resp)

        geocollections[new_name] = {
            'filepath': filepath,
            'field': 'id',
            'url': self.url + "/intersection-file",
            'is intersection': True,
            'first': collection_one,
            'second': collection_two
        }

        self.intersection(new_name, collection_one)
        self.intersection(new_name, collection_two)

    @check_alive
    def rasterstats_as_xt(self, vector, raster, name):
        """"""
        first = hash_collection(vector)
        if not first:
            raise ValueError("Can't find collection {}".format(vector))
        second = hash_collection(raster)
        if not second:
            raise ValueError("Can't find collection {}".format(raster))

        resp = requests.post(
            self.url + "/rasterstats",
            data={'vector': first, 'raster': second},
            stream=True
        )
        if resp.status_code != 200:
            raise ValueError("Server returned an error code: {}: {}".format(
                resp.status_code, resp.text))

        filepath = self._download_file(resp)
        return import_xt_from_rasterstats(filepath, name, vector)

    @check_alive
    def calculate_rasterstats(self, vector, raster):
        first = hash_collection(vector)
        if not first:
            raise ValueError("Can't find collection {}".format(vector))
        second = hash_collection(raster)
        if not second:
            raise ValueError("Can't find collection {}".format(raster))

        catalog = {obj[1] for obj in self.catalog()['files']}
        if first not in catalog:
            print("Uploading collection {}".format(vector))
            self.upload(vector)
        if second not in catalog:
            print("Uploading collection {}".format(raster))
            self.upload(raster)

        resp = requests.post(
            self.url + "/calculate-rasterstats",
            data={'vector': first, 'raster': second},
        )
        if resp.status_code == 409:
            raise AlreadyExists
        elif resp.status_code != 200:
            raise ValueError("Server returned an error code: {}: {}".format(
                resp.status_code, resp.text))
        else:
            print("Calculation job submitted.")
            return PendingJob(self.url + resp.text)

    @check_alive
    def calculate_intersection(self, collection_one, collection_two):
        first = hash_collection(collection_one)
        if not first:
            raise ValueError("Can't find collection {}".format(collection_one))
        second = hash_collection(collection_two)
        if not second:
            raise ValueError("Can't find collection {}".format(collection_two))

        catalog = {obj[1] for obj in self.catalog()['files']}
        if first not in catalog:
            print("Uploading collection {}".format(collection_one))
            self.upload(collection_one)
        if second not in catalog:
            print("Uploading collection {}".format(collection_two))
            self.upload(collection_two)

        resp = requests.post(
            self.url + "/calculate-intersection",
            data={'first': first, 'second': second},
        )
        if resp.status_code == 409:
            raise AlreadyExists
        elif resp.status_code != 200:
            raise ValueError("Server returned an error code: {}: {}".format(
                resp.status_code, resp.text))
        else:
            print("Calculation job submitted.")
            return PendingJob(self.url + resp.text)


remote = PandarusRemote()

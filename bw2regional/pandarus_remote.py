# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data import projects
from . import (
    geocollections,
    intersections,
    import_from_pandarus,
    topocollections,
)
from .utils import hash_collection, get_spatial_dataset_kind
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
        self.download_dirpath = projects.request_directory("regional")

    @property
    def alive(self):
        return requests.get(self.url).status_code == 200

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

        try:
            kind = metadata['kind']
        except KeyError:
            kind = get_spatial_dataset_kind(metadata['filepath'])

        url = self.url + "/upload"
        data = {
            'layer': metadata.get('layer') or '',
            'field': metadata.get('field') or '',
            'band': metadata.get('band') or '',
            'sha256': collection_hash,
            'kind': kind,
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
        return import_from_pandarus(filepath)

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

    @check_alive
    def area(self, collection):
        first = hash_collection(collection)
        if not first:
            raise ValueError("Can't find collection {}".format(collection))

        resp = requests.post(
            self.url + "/area",
            data={'first': first},
            stream=True
        )
        if resp.status_code == 404:
            raise NotYetCalculated("Not yet calculated; Run `.calculate_area` first.")
        elif resp.status_code != 200:
            raise ValueError("Server an error code: {}: {}".format(resp.status_code, resp.text))

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

        # Create Area
        return import_from_pandarus(filepath)

    @check_alive
    def calculate_area(self, collection):
        first = hash_collection(collection)
        if not first:
            raise ValueError("Can't find collection {}".format(collection))

        catalog = {obj[1] for obj in self.catalog()['files']}
        if first not in catalog:
            print("Uploading collection {}".format(collection))
            self.upload(collection)

        resp = requests.post(
            self.url + "/calculate-area",
            data={'first': first},
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

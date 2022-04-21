import os
import time
import uuid

import requests
import wrapt
from bw2data import config, projects

from . import geocollections, intersections, topocollections
from .errors import WindowsPathCharacterLimit
from .pandarus import import_from_pandarus, import_xt_from_rasterstats
from .utils import hash_collection


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
                if self.status not in {"failed", "finished", "forgotten"}:
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
    """Interaction with `pandarus_remote <https://github.com/cmutel/pandarus_remote>`__ web service.

    Default URL is `https://pandarus.brightway.dev`."""

    def __init__(self, url=None):
        self.url = url or "https://pandarus.brightway.dev"
        if self.url[-1] == "/":
            self.url = self.url[:-1]

    @property
    def alive(self):
        return requests.get(self.url).status_code == 200

    def _download_file(self, resp):
        assert "Content-Disposition" in resp.headers
        download_dirpath = projects.request_directory("regional")

        filepath = os.path.abspath(
            os.path.join(
                download_dirpath,
                resp.headers["Content-Disposition"].replace(
                    "attachment; filename=", ""
                ),
            )
        )

        if config._windows and len(str(filepath)) > 250:
            # Windows has an absolute limit of 255 characters in a filepath
            if len(str(os.path.abspath(download_dirpath))) > 200:
                ERROR = """Cannot safely save files in this project directory.
                The project name is too long: {} characters for complete directory path, should fewer than 200.
                The directory used for downloads is: {}
                Please start a new project with a shorter project name."""
                raise WindowsPathCharacterLimit(
                    ERROR.format(len(download_dirpath), download_dirpath)
                )
            filepath = os.path.abspath(
                os.path.join(
                    download_dirpath,
                    uuid.uuid4().hex + filepath.split(".")[-1],
                )
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

        assert "filepath" in metadata, "Can't find file for this collection"

        try:
            collection_hash = metadata["sha256"]
        except KeyError:
            collection_hash = hash_collection(collection)

        if collection_hash in {obj[1] for obj in self.catalog()["files"]}:
            raise AlreadyExists

        url = self.url + "/upload"
        data = {
            "layer": metadata.get("layer") or "",
            "field": metadata.get("field") or "",
            "band": metadata.get("band") or "",
            "sha256": collection_hash,
            "name": os.path.basename(metadata["filepath"]),
        }
        files = {"file": open(metadata["filepath"], "rb")}
        resp = requests.post(url, data=data, files=files)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise RemoteError("{}: {}".format(resp.status_code, resp.text))

    @check_alive
    def intersection(self, collection_one, collection_two):
        if (collection_one, collection_two) in intersections:
            print(
                "Skipping existing intersection: ({}, {})".format(
                    collection_one, collection_two
                )
            )
            return

        catalog = self.catalog()
        first = self.hash_and_upload(collection_one, catalog)
        second = self.hash_and_upload(collection_two, catalog)

        resp = requests.post(
            self.url + "/intersection",
            data={"first": first, "second": second},
            stream=True,
        )
        if resp.status_code == 404:
            raise NotYetCalculated(
                "Not yet calculated; Run `.calculate_intersection` first."
            )
        self.handle_errors(resp)

        filepath = self._download_file(resp)
        return import_from_pandarus(filepath)

    @check_alive
    def intersection_as_new_geocollection(
        self, collection_one, collection_two, new_name
    ):
        if new_name in geocollections:
            print("Skipping creation of existing geocollection")
            return

        catalog = self.catalog()
        first = self.hash_and_upload(collection_one, catalog)
        second = self.hash_and_upload(collection_two, catalog)

        resp = requests.post(
            self.url + "/intersection-file",
            data={"first": first, "second": second},
            stream=True,
        )
        if resp.status_code == 404:
            raise NotYetCalculated(
                "Not yet calculated; Run `.calculate_intersection` first."
            )
        self.handle_errors(resp)

        filepath = self._download_file(resp)

        geocollections[new_name] = {
            "filepath": filepath,
            "field": "id",
            "url": self.url + "/intersection-file",
            "is intersection": True,
            "first": collection_one,
            "second": collection_two,
        }

        try:
            self.intersection(new_name, collection_one)
        except NotYetCalculated:
            self.calculate_intersection(new_name, collection_one)
            print(
                """Remote is calculating intersection, run the following when done:
                  remote.intersection("{}", "{}"")""".format(
                    new_name, collection_one
                )
            )
        try:
            self.intersection(new_name, collection_two)
        except NotYetCalculated:
            self.calculate_intersection(new_name, collection_two)
            print(
                """Remote is calculating intersection, run the following when done:
                  remote.intersection("{}", "{}"")""".format(
                    new_name, collection_two
                )
            )

    @check_alive
    def rasterstats_as_xt(self, vector, raster, name):
        """ """
        catalog = self.catalog()
        first = self.hash_and_upload(vector, catalog)
        second = self.hash_and_upload(raster, catalog)

        resp = requests.post(
            self.url + "/rasterstats",
            data={"vector": first, "raster": second},
            stream=True,
        )
        self.handle_errors(resp)

        filepath = self._download_file(resp)
        return import_xt_from_rasterstats(filepath, name, vector)

    @check_alive
    def calculate_rasterstats(self, vector, raster):
        catalog = self.catalog()
        first = self.hash_and_upload(vector, catalog)
        second = self.hash_and_upload(raster, catalog)

        resp = requests.post(
            self.url + "/calculate-rasterstats",
            data={"vector": first, "raster": second},
        )
        self.handle_errors(resp)

        print("Calculation job submitted.")
        return PendingJob(self.url + resp.text)

    @check_alive
    def calculate_intersection(self, collection_one, collection_two):
        catalog = self.catalog()
        first = self.hash_and_upload(collection_one, catalog)
        second = self.hash_and_upload(collection_two, catalog)

        resp = requests.post(
            self.url + "/calculate-intersection",
            data={"first": first, "second": second},
        )
        self.handle_errors(resp)

        print("Calculation job submitted.")
        return PendingJob(self.url + resp.text)

    def hash_and_upload(self, collection, catalog=None):
        hashes = {obj[1] for obj in (catalog or self.catalog())["files"]}
        hashed = hash_collection(collection)
        if not hashed:
            raise ValueError("Can't find collection {}".format(collection))
        if hashed not in hashes:
            self.upload(collection)
        return hashed

    def handle_errors(self, response):
        if response.status_code == 409:
            raise AlreadyExists
        elif response.status_code != 200:
            raise ValueError(
                "Server returned an error code: {}: {}".format(
                    response.status_code, response.text
                )
            )


remote = PandarusRemote()

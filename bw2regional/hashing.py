import hashlib


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, "rb")
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()

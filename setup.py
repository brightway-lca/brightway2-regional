from setuptools import setup
import os


requirements = [
    "bw2calc>=2.0.dev2",
    "bw2data>=4.0.dev7",
    "constructive_geometries",
    "fiona",
    "geopandas",
    "rasterio",
    "requests",
    "shapely",
    "voluptuous",
    "wrapt",
]

v_temp = {}
with open("bw2regional/version.py") as fp:
    exec(fp.read(), v_temp)
version = ".".join((str(x) for x in v_temp["version"]))


setup(
    name="bw2regional",
    version=version,
    packages=["bw2regional", "bw2regional.lca"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license="NewBSD 3-clause; LICENSE.txt",
    url="https://github.com/brightway-lca/brightway2-regional",
    install_requires=[] if os.environ.get("READTHEDOCS") else requirements,
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)

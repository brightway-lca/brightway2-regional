from setuptools import setup
import os


requirements=[
    "brightway2",
    "bw2calc>=1.2",
    "bw2data>=2.0",
    "constructive_geometries",
    "eight",
    "fiona",
    "pandas",
    "pandarus>=1.0",
    "requests",
    "stats_arrays",
    "voluptuous",
    "wrapt",
]

rtd_requirements = ["eight", "requests"]

setup(
    name='bw2regional',
    version="0.4.1",
    packages=["bw2regional", "bw2regional.lca"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE.txt', encoding='utf-8').read(),
    url="https://bitbucket.org/cmutel/brightway2-regional",
    install_requires=[] if os.environ.get('READTHEDOCS') else requirements,
    long_description=open('README.rst', encoding='utf-8').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)

from setuptools import setup

setup(
    name='bw2regional',
    version="0.1",
    packages=["bw2regional", "bw2regional.tests"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE.txt').read(),
    url="https://bitbucket.org/cmutel/brightway2-regional",
    install_requires=[
        "brightway2",
        "bw2calc",
        "bw2data",
        "pandarus"
    ],
    long_description=open('README.rst').read(),
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
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)

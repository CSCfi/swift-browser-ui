"""."""


import setuptools
from swift_x_account_sharing import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description="Container sharing backend for Openstack Swift.",
    author=__author__,
    author_email="sampsa.penna@csc.fi",
    project_urls={
        "Source": "https://github.com/CSCfi/swift-x-account-sharing",
    },
    licnese="MIT",
    install_requires=[

    ],
    extras_require={
        "test": ["tox", "pytest", "pytest-cov", "coverage", "flake8",
                 "flake8-doctsrings", "asynctest"],
    },
    packages=[__name__],
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Intended Audience ::  Information Technology",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.7",
    ],
)

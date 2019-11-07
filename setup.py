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
        "aiohttp",
        "uvloop",
        "asyncpg",
    ],
    extras_require={
        "test": ["tox", "pytest", "pytest-cov", "coverage", "flake8",
                 "flake8-docstrings", "asynctest"],
    },
    packages=["swift_x_account_sharing", "swift_x_account_sharing.bindings"],
    platforms="any",
    entry_points={
        "console_scripts": [
            "swift-x-account-sharing=swift_x_account_sharing.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Intended Audience ::  Information Technology",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)

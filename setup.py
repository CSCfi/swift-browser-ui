import setuptools
from swift_upload_runner import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description="Swift upload / download runner for swift-browser-ui",
    author=__author__,
    author_email="sampsa.penna@csc.fi",
    project_urls={
        "Source": "https://github.com/CSCfi/swift-upload-runner",
    },
    license="MIT",
    install_requires=[
        "aiohttp",
        "python-swiftclient",
        "keystoneauth1",
        "gunicorn",
        "certifi",
        "uvloop",
        "swift-browser-ui" "@ git+https://github.com/cscfi/swift-browser-ui.git",
    ],
    extras_require={
        "test": [
            "tox",
            "pytest",
            "pytest-cov",
            "coverage",
            "tox",
            "flake8",
            "flake8-docstrings",
            "pytest-aiohttp",
            "asynctest",
            "black",
        ],
    },
    packages=[__name__],
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": [
            "swift-upload-runner=swift_upload_runner.server:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)

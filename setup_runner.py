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
        "aiohttp==3.7.4.post0",
        "requests==2.25.1",
        "python-swiftclient==3.11.1",
        "keystoneauth1==4.3.1",
        "gunicorn>=20.0.1",
        "uvloop==0.15.2",
        "certifi==2020.12.05",
        "swift-browser-ui" "@ git+https://github.com/cscfi/swift-browser-ui.git",
    ],
    extras_require={
        "test": [
            "tox==3.23.1",
            "pytest==6.2.4",
            "pytest-cov==2.12.1",
            "coverage==5.5",
            "flake8==3.9.2",
            "flake8-docstrings==1.6.0",
            "asynctest==0.13.0",
            "black==21.6b0",
            "pytest-aiohttp==0.3.0",
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

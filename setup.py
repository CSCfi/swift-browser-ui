import setuptools
from swift_browser_ui import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description="Object browser for OS_swift API",
    author=__author__,
    author_email="sampsa.penna@csc.fi",
    project_urls={
        "Source": "https://github.com/CSCfi/swift-browser-ui",
    },
    license="MIT",
    install_requires=[
        "aiohttp",
        "python-swiftclient",
        "cryptography",
        "keystoneauth1",
        "click",
        "gunicorn",
        "uvloop",
        "certifi",
    ],
    extras_require={
        "test": [
            "tox",
            "pytest",
            "pytest-cov",
            "coverage",
            "coveralls",
            "tox",
            "flake8",
            "flake8-docstrings",
            "pytest-aiohttp",
            "pytest-xdist",
            "asynctest",
        ],
        "docs": ["sphinx >= 1.4", "sphinx_rtd_theme", "selenium"],
        "ui_test": ["pytest", "selenium", "pytest-timeout"],
    },
    packages=[__name__],
    package_data={__name__: ["static/*", "static/js/*", "static/css/*", "static/img/*"]},
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": [
            "swift-browser-ui=swift_browser_ui.shell:main",
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

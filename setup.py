import setuptools
from swift_browser_ui import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description="Object browser for OS_swift API",
    author=__author__,
    project_urls={
        "Source": "https://github.com/CSCfi/swift-browser-ui",
    },
    license="MIT",
    install_requires=[
        "aiohttp==3.7.4.post0",
        "python-swiftclient==3.11.1",
        "cryptography==3.4.7",
        "keystoneauth1==4.3.1",
        "click==7.1.2",
        "gunicorn>=20.0.1",
        "uvloop==0.15.2",
        "certifi==2020.12.05",
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
        "docs": ["sphinx==3.5.4", "sphinx_rtd_theme==0.5.2", "selenium"],
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

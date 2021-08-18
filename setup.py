import setuptools
from swift_browser_ui import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description="Object browser Web UI for Openstack Swift API",
    author=__author__,
    project_urls={
        "Source": "https://github.com/CSCfi/swift-browser-ui",
    },
    license="MIT",
    install_requires=[
        "aiohttp==3.7.4.post0",
        "python-swiftclient==3.12.0",
        "cryptography==3.4.7",
        "keystoneauth1==4.3.1",
        "click==8.0.1",
        "gunicorn>=20.0.1",
        "uvloop==0.15.3",
        "certifi==2021.5.30",
        "asyncpg==0.24.0",
    ],
    extras_require={
        "test": [
            "tox==3.24.1",
            "pytest==6.2.4",
            "pytest-cov==2.12.1",
            "coverage==5.5",
            "coveralls==3.2.0",
            "flake8==3.9.2",
            "flake8-docstrings==1.6.0",
            "pytest-xdist==2.3.0",
            "asynctest==0.13.0",
            "black==21.7b0",
        ],
        "docs": ["sphinx==4.1.2", "sphinx_rtd_theme==0.5.2"],
        "ui_test": ["pytest==6.2.4", "pytest-timeout==1.4.2"],
    },
    packages=setuptools.find_packages(),
    package_data={
        __name__: ["ui/static/*", "ui/static/js/*", "ui/static/css/*", "ui/static/img/*"]
    },
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": [
            "swift-browser-ui=swift_browser_ui.launcher:run_ui",
            "swift-x-account-sharing=swift_browser_ui.launcher:run_sharing",
            "swift-sharing-request=swift_browser_ui.launcher:run_request",
            "swift-upload-runner=swift_browser_ui.launcher:run_upload",
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

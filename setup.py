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
        "aiohttp==3.8.3",
        "aiohttp-session==2.12.0",
        "aioredis==2.0.1",
        "asyncpg==0.27.0",
        "certifi==2022.9.24",
        "click==8.1.3",
        "cryptography==38.0.3",
        "gunicorn==20.1.0",
        "keystoneauth1==5.0.0",
        "oidcrp==2.1.4",
        "python-swiftclient==4.1.0",
        "uvloop==0.17.0",
    ],
    extras_require={
        "test": [
            "black==22.10.0",
            "flake8==6.0.0",
            "coverage==6.5.0",
            "flake8-docstrings==1.6.0",
            "pytest==7.2.0",
            "pytest-cov==4.0.0",
            "pytest-xdist==3.0.2",
            "tox==3.27.1",
        ],
        "docs": ["sphinx==5.3.0", "sphinx_rtd_theme==1.1.1"],
        "ui_test": ["pytest==7.2.0", "pytest-timeout==2.1.0"],
    },
    packages=setuptools.find_packages(),
    package_data={
        __name__: [
            "ui/static/*",
            "ui/static/js/*",
            "ui/static/sw/*",
            "ui/static/css/*",
            "ui/static/img/*",
        ]
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

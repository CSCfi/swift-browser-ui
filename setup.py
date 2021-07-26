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
        "python-swiftclient==3.12.0",
        "cryptography==3.4.7",
        "keystoneauth1==4.3.1",
        "click==8.0.1",
        "gunicorn>=20.0.1",
        "uvloop==0.15.2",
        "certifi==2021.5.30",
    ],
    extras_require={
        "test": [
            "tox==3.23.1",
            "pytest==6.2.4",
            "pytest-cov==2.12.1",
            "coverage==5.5",
            "coveralls==3.2.0",
            "flake8==3.9.2",
            "flake8-docstrings==1.6.0",
            "pytest-xdist==2.3.0",
            "asynctest==0.13.0",
            "black==21.6b0",
        ],
        "docs": ["sphinx==4.0.3", "sphinx_rtd_theme==0.5.2", "selenium==3.141.0"],
        "ui_test": ["pytest==6.2.4", "selenium==3.141.0 ", "pytest-timeout==1.4.2"],
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

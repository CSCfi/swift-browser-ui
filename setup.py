import setuptools
from s3browser import __name__, __version__, __author__


setuptools.setup(
    name=__name__,
    version=__version__,
    description='Object browser for OS_swift API',
    author=__author__,
    author_email="sampsa.penna@csc.fi",
    license='MIT',
    install_requires=[
        'aiohttp',
        'boto3',
        'python-swiftclient',
        'cryptography',
        'keystoneauth1',
        'click',
    ],
    extras_require={
          'test': ['tox', 'pytest', 'pytest-cov', 'coverage', 'coveralls',
                   'pytest-asyncio', 'tox',
                   'flake8', 'flake8-docstrings', 'pytest-aiohttp', 'pytest-xdist']},
    packages=[__name__],
)

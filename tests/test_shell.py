"""
Module for testing the project command line interface
"""


from click.testing import CliRunner

from s3browser.shell import cli, start


def test_shell_cli():
    """
    Test that the cli group function runs fully with the wanted parameters
    """
    # Test if the cli group runs as it should
    runner = CliRunner()
    runner.invoke(
        cli, [
            '--verbose',
            '--debug',
            '--logfile',
            '/dev/null',
        ]
    )


def test_shell_start():
    """
    Test that the cli start function runs fully with the wanted parameters
    """
    # Test if the start command runs as it should
    runner = CliRunner()
    runner.invoke(
        start, [
            '--port', '8080',
            '--static-directory', 's3browser_frontend',
            '--auth-endpoint-url', 'https://localhost:5001/v3',
            '--has-trust',
            '--siwft-endpoint-url', 'https://localhost:443/swift/v1',
            '--dry-run',  # dry run since we're not testing the server
        ]
    )

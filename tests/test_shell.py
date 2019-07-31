"""Module for testing the project command line interface."""

import unittest
from click.testing import CliRunner

from s3browser.shell import cli, start


class TestService(unittest.TestCase):
    """Test cli runs."""

    def setUp(self):
        """Set up runner for cli."""
        self.runner = CliRunner()

    def test_shell_cli(self):
        """Test that the cli group function runs with the wanted parameters."""
        # Test if the cli group runs as it should
        result = self.runner.invoke(
            cli, [
                '--verbose',
                '--debug',
                '--logfile',
                '/dev/null',
            ]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn('Missing command', result.output)

    def test_shell_start_dry(self):
        """Test that the cli start function runs with dry-run."""
        # Test if the start command runs as it should
        result = self.runner.invoke(
            start, [
                '--port', '8080',
                '--auth-endpoint-url', 'https://localhost:5001/v3',
                '--has-trust',
                '--dry-run',  # dry run since we're not testing the server
            ]
        )

        self.assertEqual(result.exit_code, 0)

    def test_shell_version(self):
        """Test that the cli version."""
        # Test if the start command runs as it should
        result = self.runner.invoke(
            cli, [
                '--version',
            ]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn('s3browser, version ', result.output)

    @unittest.mock.patch('s3browser.shell.servinit')
    def test_shell_start(self, mock_server):
        """Test that the cli start function runs with the wanted parameters."""
        # Test if the start command runs as it should
        self.runner.invoke(
            start, [
                '--port', '8080',
                '--auth-endpoint-url', 'https://localhost:5001/v3',
                '--has-trust',
            ]
        )
        mock_server.assert_called()

    def test_shell_set_verbose(self):
        """Test that the cli start function runs with verbose."""
        # Test if the start command runs as it should
        result = self.runner.invoke(
            cli, [
                '--verbose',
                '--debug',
                '--logfile',
                '/dev/null',
                'start',
                '--dry-run',  # dry run since we're not testing the server
            ]
        )
        self.assertEqual(result.exit_code, 0)

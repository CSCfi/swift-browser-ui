"""
CLI for configuring and launching the server.
"""


from .__init__ import VERSION
import click
import logging

from .settings import setd
from .server import servinit, run_server_insecure
from ._convenience import setup_logging as conv_setup_logging


@click.group()
@click.version_option(
    version=VERSION, prog_name="s3browser"
)
@click.option(
    '-v', '--verbose', is_flag=True, default=False,
    help='Increase program verbosity.'
)
@click.option(
    '-D', '--debug', is_flag=True, default=False,
    help='Enable debug level logging.'
)
@click.option(
    '--logfile', default=None, type=str,
    help='Write program logs to a file.'
)
def cli(verbose, debug, logfile):
    """
    Command line interface for managing s3browser.
    """
    logging.basicConfig()
    # set version
    setd['version'] = VERSION
    # set verbose
    if verbose:
        setd['verbose'] = True
        logging.root.setLevel(logging.INFO)
        logging.info(
            'Set logging level to info. ' +
            'Reason: got flag "--verbose"'
        )
    # set debug
    if debug:
        setd['debug'] = True
        logging.root.setLevel(logging.DEBUG)
        logging.info(
            'Set logging level to debug. ' +
            'Reason: got flag "--debug"'
        )
    # set logfile
    if logfile:
        setd['logfile'] = logfile
        new_handler = logging.FileHandler(logfile)
        new_handler.setFormatter(
            logging.Formatter(logging.BASIC_FORMAT)
        )
        logging.root.addHandler(
            new_handler
        )
        logging.info(
            'Save log information to the file {0}'.format(logfile) +
            ' – Reason: got option "--logfile"'
        )
    conv_setup_logging()


@cli.command()
@click.option(
    '-p', '--port', default=8080,
    help='Set the port the server is run on.'
)
@click.option(
    '--static-directory', default=None,
    help='Set the static content directory'
)
@click.option(
    '--auth-endpoint-url', default=None, type=str,
    help="Endpoint for the Openstack keystone API in use."
)
@click.option(
    '--has-trust', is_flag=True, default=False,
    help=('Flag if the program is listed on the trusted_dashboards in the' +
          ' specified address.')
)
@click.option(
    '--swift-endpoint-url', default=None, type=str,
    help="Endpoint url for the Openstack swift API in use."
)
@click.option(
    '--dry-run', is_flag=True, default=False, hidden=True,
)
@click.option(
    '--set-origin-address', default=None, type=str,
    help="Set the address that the program will be redirected to from WebSSO"
)
def start(
    port,
    static_directory,
    auth_endpoint_url,
    has_trust,
    swift_endpoint_url,
    dry_run,
    set_origin_address,
):
    """
    Start the browser backend and server
    """
    logging.debug(
        "Current settings dictionary:\n" + str(setd)
    )
    if port:
        logging.info(
            "Set the running port as %s.", str(port)
        )
        setd['port'] = port
    if static_directory:
        logging.info(
            "Set the static directory location as %s.",
            static_directory
        )
        setd['static_directory'] = static_directory
    if auth_endpoint_url:
        logging.info(
            "Set the authorization endpoint url to %s.",
            auth_endpoint_url
        )
        setd['auth_endpoint_url'] = auth_endpoint_url
    if has_trust:
        logging.info(
            "Assuming the program is trusted on the endpoint? %s",
            str(has_trust)
        )
        setd['has_trust'] = True
    if swift_endpoint_url:
        logging.info(
            "Set object storage endpoint as %s.",
            swift_endpoint_url
        )
        setd['swift_endpoint_url'] = swift_endpoint_url
    if dry_run:
        logging.debug(
            "Not running server, dry-run flagged."
        )
    if set_origin_address:
        logging.info(
            "Setting login return address to %s",
            set_origin_address
        )
        setd['origin_address'] = set_origin_address
    logging.debug(
        "Running settings directory:\n" + str(setd)
    )
    if not dry_run:
        run_server_insecure(servinit())


@cli.command()
def install():
    """
    Install the browser backend (implemented in the future)
    """
    click.echo('Install the program')


if __name__ == "__main__":
    cli(
        auto_envvar_prefix='BROWSER'
    )

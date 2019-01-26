from contextlib import contextmanager
import atexit
import logging
import time

import docker

from ._version import __version__


#: containers that have been started and need to be removed
_containers = set()


def _exit_handler():
    """cleanup any remaining containers"""
    for container in _containers:
        logging.debug('atexit handler: cleaning up container %r', container)
        try:
            container.kill()
        except docker.errors.APIError:
            # Ignore errors when killing containers because they may already be
            # dead
            pass


atexit.register(_exit_handler)


def postgres(database=None, user=None, password=None, port=None,
             version=None, wait_time=30):
    """
    Start a new postgres instance in docker. The container will be started
    in a detached state and automatically cleaned up when this python process
    exits.

    Parameters
    ----------
    database : str
        Name of the database
    user : str
        User name of the default user
    password : str
        Password of the default user
    port : int
        Port number to listen on. By default a free port will be automatically
        be selected
    version : str
        Version of postgres to start. Defaults to the lastest version on the
        host
    wait_time : float
        Wait at most `wait_time` seconds for the postgres server to be ready

    Returns
    -------
    uri, container -- uri is a postgresql URI for connecting to the container,
        container is a docker container instance for controlling the instance
    """
    if database is None:
        database = 'mydb'
    if user is None:
        user = 'postgres'
    if password is None:
        password = 'postgres'
    if port is None:
        port = 0
    if version is None:
        version = 'latest'
    pg_env = {
        'POSTGRES_DB': database,
        'POSTGRES_USER': user,
        'POSTGRES_PASSWORD': password
    }
    # expose the internal port to any open port on the host
    pg_ports = {
        '5432/tcp': port
    }
    client = docker.from_env()
    container = client.containers.run(
        'postgres:' + version,
        remove=True,
        environment=pg_env,
        ports=pg_ports,
        detach=True)
    _containers.add(container)
    container.reload()
    actual_port = (
        container.attrs
        ['NetworkSettings']
        ['Ports']
        ['5432/tcp']
        [0]
        ['HostPort'])
    uri = _postgres_uri(user, password, actual_port, database)
    if wait_time > 0:
        wait_uri = _postgres_uri(user, password, 5432, database)
        _wait_for_port(container, wait_uri, wait_time)
    return uri, container


@contextmanager
def postgres_ctx(*args, **kwargs):
    """
    Postgres context manager that automatically cleans up the instance on exit
    """
    uri, container = postgres(*args, **kwargs)
    yield uri
    container.stop()
    _containers.remove(container)


def _postgres_uri(user, password, port, database):
    return 'postgresql://{user}:{password}@localhost:{port}/{database}'.format(
        user=user,
        password=password,
        port=port,
        database=database)


def _wait_for_port(container, uri, timeout):
    """Wait until the specified port can be connected to"""
    now = time.time()
    while time.time() - now < timeout:
        result, _ = container.exec_run(
            ['psql', '-qAt', uri, '-c', 'SELECT 1;'])
        if result == 0:
            return
    raise TimeoutError(
        'Failed to connect to port %r after waiting %r seconds'.format(
            port, timeout))

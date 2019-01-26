import psycopg2
import pytest

import ephemeral_postgres as ep


def test_mock_postgres(mocker):
    """
    test starting postgres with non-default parameters and mocked docker
    """
    docker = mocker.patch('ephemeral_postgres.docker')
    uri, container = ep.postgres(
        database='db',
        user='user',
        password='pass',
        version='19.5',
        port=1234,
        wait_time=0)
    docker.from_env().containers.run.assert_called_once_with(
        'postgres:19.5',
        detach=True,
        environment={
            'POSTGRES_DB': 'db',
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'pass'
        },
        ports={'5432/tcp': 1234},
        remove=True)
    # port is retrieved at runtime
    actual_port = (
        container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort'])
    assert uri == 'postgresql://user:pass@localhost:{}/db'.format(
        actual_port)


def test_mock_postgres_defaults(mocker):
    """
    test starting postgres with default parameters and mocked docker
    """
    docker = mocker.patch('ephemeral_postgres.docker')
    uri, container = ep.postgres(wait_time=0)
    docker.from_env().containers.run.assert_called_once_with(
        'postgres:latest',
        detach=True,
        environment={
            'POSTGRES_DB': 'mydb',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'postgres'
        },
        ports={'5432/tcp': 0},
        remove=True)
    # port is retrieved at runtime
    actual_port = (
        container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort'])
    assert uri == 'postgresql://postgres:postgres@localhost:{}/mydb'.format(
        actual_port)


def test_postgres():
    """
    test actually starting postgres
    """
    with ep.postgres_ctx() as uri:
        con = psycopg2.connect(uri)
        cur = con.cursor()

        # initialize a table
        cur.execute(
            '''
            CREATE TABLE cogs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
            ''')
        con.commit()

        # add some values
        sql = 'INSERT INTO cogs(name) VALUES(%s)'
        names = ('wheel', 'screw', 'bolt')
        # convert names to a list of tuples for executing
        names_list = [(name, ) for name in names]
        cur.executemany(sql, names_list)
        con.commit()
        cur.close()
        con.close()

        # start a new connection
        con = psycopg2.connect(uri)
        cur = con.cursor()
        cur.execute('SELECT * FROM cogs ORDER BY id')
        rows = cur.fetchall()
        assert rows == [
            (1, 'wheel'),
            (2, 'screw'),
            (3, 'bolt')]
        cur.close()
        con.close()

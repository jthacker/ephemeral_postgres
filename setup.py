from distutils.util import convert_path
from setuptools import find_packages, setup


def get_version():
    main_ns = {}
    ver_path = convert_path('ephemeral_postgres/_version.py')
    with open(ver_path) as ver_file:
        exec(ver_file.read(), main_ns)
    return main_ns['__version__']


def get_readme():
    from io import open
    from os import path
    this_dir = path.abspath(path.dirname(__file__))
    with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
        return f.read()


_version = get_version()


_extras = {
    'test': [
        'flake8',
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'psycopg2-binary'
    ]
}


BASE_URL = 'https://github.com/jthacker/ephemeral_postgres'

setup(
    name='ephemeral-postgres',
    description='Start an ephemeral postgres instance for easy testing',
    packages=find_packages(),
    version=_version,
    url=BASE_URL,
    download_url=BASE_URL + '/archive/v{}.tar.gz'.format(_version),
    author='jthacker',
    author_email='thacker.jon@gmail.com',
    keywords=['postgres', 'postgresql', 'testing', 'docker'],
    classifiers=[],
    extras_require=_extras,
    install_requires=[
        'docker >= 3',
    ],
    setup_requires=['pytest-runner'],
    tests_require=_extras['test'],
    entry_points={},
    long_description=get_readme(),
    long_description_content_type='text/markdown'
)

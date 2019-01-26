# ephemeral-postgres

[![Build Status](https://travis-ci.org/jthacker/ephemeral_postgres.svg?branch=master)](https://travis-ci.org/jthacker/ephemeral_postgres)

ephemeral-postgres is a python package for easily setting up, testing, and
finally tearing down postgres instances. It can be easily integrated in most
test suites but has been primarily used with pytest.


## Installation
```bash
pip install ephemeral-postgres
```

## Example
```python
import ephemeral_postgres
import psycopg2

with ephemeral_postgres.postgres() as uri:
    con = psycopg2.connect(uri)
    cur = con.cursor()
    cur.execute('select * from pg_database')
    for row in cur.fetchall():
        print(row)
```

## Developing
```bash
pip install -e .[test]

# run unit tests
pytest
```



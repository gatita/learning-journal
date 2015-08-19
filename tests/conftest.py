import os
import pytest
from pytest_bdd import given
from sqlalchemy import create_engine

import journal
from test_journal import login_helper


TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://gracehatamyar@localhost:5432/test-learning-journal'
    )
os.environ['DATABASE_URL'] = TEST_DATABASE_URL


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine(TEST_DATABASE_URL)
    journal.Base.metadata.create_all(engine)
    # create connection to our database
    # this opens a transaction that last for the scope
    # of the entire session
    connection = engine.connect()
    journal.DBSession.registry.clear()
    # bind this in the name space  of journal
    journal.DBSession.configure(bind=connection)
    journal.Base.metadata.bind = engine
    request.addfinalizer(journal.Base.metadata.drop_all)
    return connection


@pytest.fixture()
def db_session(request, connection):
    # starts a new transaction inside the already open transaction
    from transaction import abort
    trans = connection.begin()
    # every test has a transaction that's open for the duration
    # of the test, and rollsback when the test is completed
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from journal import DBSession
    return DBSession


@pytest.fixture()
def app(db_session):
    from journal import main
    from webtest import TestApp
    app = main()
    return TestApp(app)


@pytest.fixture()
def homepage(app):
    response = app.get('/')
    return response


@pytest.fixture()
def entry_page(homepage):
    redirect = homepage.click(description='Read', index=0)
    return redirect


@pytest.fixture()
def edit_page(app):
    response = app.get('/edit/0', status=403)
    return response


# @pytest.fixture()
# def author(app):
#     username, password = ('admin', 'secret')
#     login_helper(username, password, app)
#     response = app.get('/')
#     return response


# @pytest.fixture()
# def edit_page_author(author):
#     response = app.get('/edit/0')
#     return response

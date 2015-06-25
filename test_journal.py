# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://gracehatamyar@localhost:5432/test-learning-journal'
    )
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['TESTING'] = "True"

import journal


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine(TEST_DATABASE_URL)
    journal.Base.metadata.create_all(engine)
    connection = engine.connect()
    journal.DBSession.registry.clear()
    journal.DBSession.configure(bind=connection)
    journal.Base.metadata.bind = engine
    request.addfinalizer(journal.Base.metadata.drop_all)
    return connection


@pytest.fixture()
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from journal import DBSession
    return DBSession


def test_write_entry(db_session):
    kwargs = {'title': "Test Title", 'text': "Test entry text"}
    kwargs['session'] = db_session
    # first, assert that there are no entries in the db
    assert db_session.query(journal.Entry).count() == 0
    # now, create an entry using the 'write' class method
    entry = journal.Entry.write(**kwargs)

    # the entry we get back ought to be an instance of Entry
    assert isinstance(entry, journal.Entry)

    # id and created are generated automatically, but only on
    # writing to the database
    auto_fields = ['id', 'created']
    for field in auto_fields:
        assert getattr(entry, field, None) is None

    # flush the session to "write" the data to the database
    db_session.flush()

    # now, we should have one entry:
    assert db_session.query(journal.Entry).count() == 1
    for field in kwargs:
        if field != 'session':
            assert getattr(entry, field, '') == kwargs[field]

    # id and created should be set automatically upon writing
    # to db
    for auto in ['id', 'created']:
        assert getattr(entry, auto, None) is not None


def test_title_not_null(db_session):
    bad_data = {'text': "Test entry text"}
    journal.Entry.write(session=db_session, **bad_data)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_entry_no_text_fails(db_session):
    bad_data = {'title': 'Test title'}
    journal.Entry.write(session=db_session, **bad_data)
    with pytest.raises(IntegrityError):
        db_session.flush()


  
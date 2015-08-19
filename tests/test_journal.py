# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from pyramid import testing
from cryptacular.bcrypt import BCRYPTPasswordManager

TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://gracehatamyar@localhost:5432/test-learning-journal'
    )
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['TESTING'] = "True"

import journal


@pytest.fixture()
def entry(db_session):
    entry = journal.Entry.write(
        title='Test Title',
        text='Test Entry Text',
        session=db_session)
    db_session.flush()
    return entry


@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)

    return req


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


def test_read_entries_empty(db_session):
    entries = journal.Entry.all()
    assert len(entries) == 0


def test_read_entries_one(db_session):
    title_template = "Title {}"
    text_template = "Entry Text {}"

    # write three entries, with order clear in the title and text
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session)
        db_session.flush()
    entries = journal.Entry.all(session=db_session)
    assert len(entries) == 3
    assert entries[0].title > entries[1].title > entries[2].title
    for entry in entries:
        assert isinstance(entry, journal.Entry)


def test_empty_listing(app):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    expected = 'No entries here so far'
    assert expected in actual


def test_listing(app, entry):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    expected = getattr(entry, 'title', 'absent')
    assert expected in actual


def test_post_to_add_view(app):
    login_helper('admin', 'secret', app)
    entry_data = {
        'title': 'Hello there',
        'text': 'This is post',
    }
    response = app.post('/create', params=entry_data)
    redirected = response.follow()
    actual = redirected.body
    assert entry_data['title'] in actual
    assert entry_data['text'] not in actual


def test_add_no_params(app):
    response = app.post('/create', status=403)
    assert response.status_code == 403


def test_do_login_success(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    assert do_login(auth_req)


def test_do_login_bad_pass(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'wrong'}
    assert not do_login(auth_req)


def test_do_login_bad_user(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'bad', 'password': 'secret'}
    assert not do_login(auth_req)


def test_do_login_missing_params(auth_req):
    from journal import do_login
    for params in ({'username': 'admin'}, {'password': 'secret'}):
        auth_req.params = params
        with pytest.raises(ValueError):
            do_login(auth_req)


BTN = '<input id="submit-button" type="submit" value="Share" name="submit"/>'


def login_helper(username, password, app):
    """encapsulate app login for reuse in tests

    Accept all status codes so that we can make assertions in tests
    """
    login_data = {'username': username, 'password': password}
    return app.post('/login', params=login_data, status='*')


def test_login_success(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    assert response.status_code == 200
    assert "Add new entry" in response.body


def test_login_fails(app):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password, app)
    assert response.status_code == 200
    actual = response.body
    assert "Login Failed" in actual
    assert "Add new entry" not in actual


def test_login_renderer(app):
    response = app.get('/', status=200)
    redirect = response.click(linkid='login')
    form = redirect.form
    for field in ['username', 'password']:
        assert field in form.fields


def test_logout(app):
    # re-use existing code to ensure we are logged in when we begin
    test_login_success(app)
    redirect = app.get('/logout', status="3*")
    response = redirect.follow()
    assert response.status_code == 200
    actual = response.body
    assert "Add new entry" not in actual


def test_forbidden_anonymous_create_request(app):
    response = app.get('/create', status=403)


def test_add_returned_after_authenticated_create_request(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = app.get('/create', status=200)
    assert BTN in response


def test_add_new_entry_btn_after_login(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    redirect = response.click(linkid='add-new')
    assert BTN in redirect


# add test to test by_id control
def test_by_id(app):
    pass

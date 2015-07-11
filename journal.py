# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json
import os
import markdown
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DBAPIError
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import remember, forget
from waitress import serve
from zope.sqlalchemy import ZopeTransactionExtension
from cryptacular.bcrypt import BCRYPTPasswordManager


HERE = os.path.dirname(os.path.abspath(__file__))


DBSession = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension())
)

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://gracehatamyar@localhost:5432/learning-journal'
)

Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.Unicode(127), nullable=False)
    text = sa.Column(sa.UnicodeText, nullable=False)
    created = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            title=self.title,
            text=markdown.markdown(
                (self.text), extensions=['codehilite', 'fenced_code']
                ),
            created=self.created.strftime('%b. %d, %Y'),
            )

    @classmethod
    def write(cls, title=None, text=None, session=None):
        if session is None:
            session = DBSession
        instance = cls(title=title, text=text)
        session.add(instance)
        return instance

    @classmethod
    def all(cls, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).order_by(cls.created.desc()).all()

    # new method to query Entry for a particular entry
    @classmethod
    def by_id(cls, pk, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).get(pk)

    @classmethod
    def update(cls, pk, title, text, session=None):
        if session is None:
            session = DBSession
        entry = cls.by_id(pk, session)
        entry.title = title
        entry.text = text


def init_db():
    engine = sa.create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required')

    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


@view_config(route_name='home', renderer='templates/list.jinja2')
def list_view(request):
    entries = Entry.all()
    return {'entries': entries}


@view_config(route_name='update', request_method='POST')
def update(request):
    pk = request.matchdict['id']
    title = request.params.get('title')
    text = request.params.get('text')
    Entry.update(pk, title, text)
    return HTTPFound(request.route_url('home'))


@view_config(context=DBAPIError)
def db_exception(context, request):
    response = Response(context.message)
    response.status_int = 500
    return response


@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = 'Login Failed'
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name='create', xhr=True, renderer='json')
@view_config(route_name='create', renderer='templates/create.jinja2')
def create(request):
    # change to error forbidden
    if not request.authenticated_userid:
        return HTTPFound(request.route_url('login'))
    if request.method == 'POST':
        session = DBSession
        title = request.params.get('title')
        text = request.params.get('text')
        entry = Entry.write(title=title, text=text)
        session.flush()
        if 'HTTP_X_REQUESTED_WITH' in request.environ:
            return entry
        return HTTPFound(request.route_url('home'))
    return {}


@view_config(route_name='entry', renderer='templates/entry.jinja2')
def entry(request):
    pk = request.matchdict['id']
    entry = Entry.by_id(pk)
    md = markdown.markdown(
        (entry.text), extensions=['codehilite', 'fenced_code']
    )
    return {'entry': entry, 'md': md}


# add edit rendered
@view_config(route_name='edit', renderer='templates/edit.jinja2')
def edit(request):
    pk = request.matchdict['id']
    entry = Entry.by_id(pk)
    return {'entry': entry}


def main():
    """ Create a configured wsgi app """
    settings = {}
    debug = os.environ.get('DEBUG', True)
    settings['reload_all'] = debug
    settings['debug_all'] = debug
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret')
    )
    if not os.environ.get('TESTING', False):
        # only bind the session if we are not testing
        engine = sa.create_engine(DATABASE_URL)
        DBSession.configure(bind=engine)
    # add a secret value for auth rkt signing
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'itsaseekrit')
    # configuration setup
    config = Configurator(
        settings=settings,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
            ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.add_static_view('static', os.path.join(HERE, 'static'))
    config.add_static_view('img', os.path.join(HERE, 'img'))
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('create', '/create')
    config.add_route('edit', '/edit/{id}')
    config.add_route('entry', '/entry/{id}')
    config.add_route('update', '/update/{id}')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)

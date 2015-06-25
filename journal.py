# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import os
from pyramid.config import Configurator
from pyramid.view import view_config
from waitress import serve
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
# from pyramid.httpexceptions import HTTPNotFound

DBSession = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension()))


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

    @classmethod
    def write(cls, title=None, text=None, session=None):
        if session is None:
            session = DBSession
        instance = cls(title=title, text=text)
        session.add(instance)
        return instance


def init_db():
    engine = sa.create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)


@view_config(route_name='home', renderer='templates/test.jinja2')
def home(request):
    return {'one': 'two'}


# @view_config(route_name='other', renderer='string')
# def other(request):
#     # import pdb; pdb.set_trace()
#     return request.matchdict


def main():
    """ Create a configured wsgi app """
    settings = {}
    debug = os.environ.get('DEBUG', True)
    settings['reload_all'] = debug
    settings['debug_all'] = debug
    if not os.environ.get('TESTING', False):
        # only bind the session if we are not testing
        engine = sa.create_engine(DATABASE_URL)
        DBSession.configure(bind=engine)
    # configuration setup
    config = Configurator(
        settings=settings
    )
    config.include('pyramid_tm')
    # config.include('pyramid_jinja2')
    config.add_route('home', '/')
    # config.add_route('other', '/other/{special_val}')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)

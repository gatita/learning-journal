# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
import journal


@scenario(
    'features/homepage.feature',
    'The Homepage lists entries for anonymous users'
)
def test_home_listing_as_anon():
    pass


@given('an anonymous user')
def an_anonymous_user(app):
    pass


@given('a list of three entries')
# this depends on db_session bc we want to mutate the session
def create_entries(db_session):
    title_template = "Title {}"
    text_template = "Entry Text {}"
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session)
        db_session.flush()


@when('the user visits the homepage')
def go_to_homepage(homepage):
    pass


@then('they see a list of 3 entries')
def check_entry_list(homepage):
    html = homepage.html
    entries = html.find_all('article', class_='post-listing')
    assert len(entries) == 3


@scenario(
    'features/detail.feature',
    'The Detail page shows a complete entry to anonymous users'
)
def test_detail_page_as_anon():
    pass


# given an anonymous user, defined above, AND
@given('a permalink for an entry')
def generate_permalink_from_anchor():
    pass


@when('the user visits the permalink')
def create_entries_with_permalinks():
    pass


@then('they see a detailed view of the entry')
def check_detail_view():
    pass


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
from pyramid import testing
import journal
from test_journal import login_helper


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
    """ Tests that GIVEN an anonymous user, and GIVEN a list of
    three entries, WHEN the user visits the homepage, and WHEN
    the user clicks on an entry's permalink, THEN they seee a
    detailed view of the entry.
    """
    pass


@when("the user clicks on an entry's permalink")
def go_to_entry_page(entry_page):
    pass


@then('they see a detailed view of the entry')
def check_entry_view(entry_page):
    html = entry_page.html
    title = html.find('h2', id='entry-title')
    assert 'Title 2' in title


@scenario(
    'features/edit.feature',
    'The Edit page is forbidden for anonymous users'
)
def test_edit_page_as_anon():
    pass


@when('the user visits the edit page for an entry')
def view_edit_page(edit_page):
    pass


@then('a 403 Forbidden is raised')
def check_edit_page_form_anon(edit_page):
    assert edit_page.status_code == 403


@scenario(
    'features/edit.feature',
    'The Edit page shows an update form to author users'
)
def test_edit_page_as_author():
    pass


@given('an author user')
def an_author_user(app):
    response = login_helper('admin', 'secret', app)
    redirect = response.follow()
    return redirect


@then('they see the edit form')
def check_edit_page_author(edit_page):
    html = edit_page.html
    edit_form = html.find('section', id='entry-form')
    assert edit_form

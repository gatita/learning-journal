Feature: Edit Page
    A prepopulated form for an entry where its contents can be edited


Scenario: The Edit page redirects to login for anonymous users
    Given an anonymous user
    And a list of three entries
    When the user visits the edit page for an entry
    Then they do not see the edit form
    Then they see the login form


Scenario: The Edit page shows an update form to author users
    Given an author user
    And a list of three entries
    When the user visits the edit page for an entry
    Then they see the edit form
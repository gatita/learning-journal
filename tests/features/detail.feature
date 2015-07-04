Feature: Detail Page
    A permalink for each entry where it can be viewed in detail


Scenario: The Detail page shows an entire individual entry for anonymous users
    Given an anonymous user
    And a permalink for an entry
    When the user visits the permalink
    Then they see a detailed view of the entry
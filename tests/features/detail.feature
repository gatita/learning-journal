Feature: Detail Page
    A permalink for each entry where it can be viewed in detail


Scenario: The Detail page shows a complete entry to anonymous users
    Given an anonymous user
    And a list of three entries
    When the user visits the homepage
    When the user clicks on an entry's permalink
    Then they see a detailed view of the entry
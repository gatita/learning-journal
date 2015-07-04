Feature: Homepage
    A listing of entries from the learning journal in reverse 
    chronological order


Scenario: The Homepage lists entries for anonymous users
    Given an anonymous user
    And a list of three entries
    When the user visits the homepage
    Then they see a list of 3 entries
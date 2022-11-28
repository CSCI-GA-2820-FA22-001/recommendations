Feature: The recommendation service back-end
    As a recommendation service user
    I need a RESTful recommendation service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | name       | recommendation_id | recommendation_name | type  | number_of_likes   |
        | fido       | 1      | AA      | CROSSSELL    | 2 |
        | kitty      | 2      | AB      | UPSELL  | 3 |
        | leo        | 3     | AC     |  ACCESSORY    | 4 |
        | sammy      | 2    | AA      | UPSELL | 5 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should not see "reco" in the results

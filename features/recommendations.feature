Feature: The recommendation store service back-end
    As a Recommendation Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my recommendations

Background:
    Given the store has following recommendations
        | name       | recommendation_id | recommendation_name | type  | number_of_likes   |
        | fido       | 1     | AA      | CROSSSELL    | 2 |
        | kitty      | 2     | AB      | UPSELL       | 3 |
        | leo        | 3     | AB      | UPSELL       | 4 |
        | las        | 4     | AC      | CROSSSELL    | 5 |
        | lays       | 5     | AC      | ACCESSORY    | 2 |
        | ways       | 6     | AC      | ACCESSORY    | 3 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all pets
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the result
    And I should see "kitty" in the result
    And I should see "leo" in the result
    And I should see "las" in the result
    And I should see "lays" in the result
    And I should see "ways" in the result

Feature: The recommendation service back-end
    As a recommendation service user
    I need a RESTful recommendation service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | name       | product_id       | recommendation_id | recommendation_name | type  | number_of_likes   |
        | fido       | 1       | 1      | AA      | CROSSSELL    | 2 |
        | kitty      | 3       | 2      | AB      | UPSELL  | 3 |
        | leo        | 2       | 3     | AC     |  ACCESSORY    | 4 |
        | sammy      | 1       | 2    | AA      | UPSELL | 5 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "Name" to "Happy"
    And I set the "Product Id" to "3"
    And I set the "Recommendation Id" to "2"
    And I set the "Recommendation Name" to "Happiness"
    And I select "Cross Sell" in the "Type" dropdown
    And I set the "Number Of Likes" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Type" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Happy" in the "Name" field
    And I should see "3" in the "Product Id" field
    And I should see "Happiness" in the "Recommendation Name" field
    And I should see "Cross Sell" in the "Type" dropdown
    And I should see "4" in the "Number Of Likes" field
    And I should see "2" in the "Recommendation Id" field

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should not see "reco" in the results


Scenario: List all recommendations by name
    When I visit the "Home Page"
    And I set the "name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should not see "kitty" in the results

Scenario: List all recommendations by type
    When I visit the "Home Page"
    And I select "Cross Sell" in the "type" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should not see "kitty" in the results

Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the "Name" field
    And I should see "Cross Sell" in the "Type" dropdown
    When I change "Name" to "Boxer"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Boxer" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Boxer" in the results
    And I should not see "fido" in the results

Scenario: Like and Dislike a recommendation
    When I visit the "Home Page"
    And I set the "Name" to "Happy"
    And I set the "Product Id" to "2"
    And I set the "Recommendation Id" to "2"
    And I set the "Recommendation Name" to "Happiness"
    And I select "Cross Sell" in the "Type" dropdown
    And I set the "Number Of Likes" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "like" button
    Then I should see "5" in the "Number of Likes" field
    When I press the "dislike" button
    Then I should see "4" in the "Number of Likes" field

Scenario: Delete a Recommendation
    When I visit the "Home Page"
    And I set the "Name" to "Happy"
    And I set the "Product Id" to "2"
    And I set the "Recommendation Id" to "2"
    And I set the "Recommendation Name" to "Happiness"
    And I select "Cross Sell" in the "Type" dropdown
    And I set the "Number Of Likes" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Type" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Happy" in the "Name" field
    And I should see "Happiness" in the "Recommendation Name" field
    And I should see "Cross Sell" in the "Type" dropdown
    And I should see "4" in the "Number Of Likes" field
    And I should see "2" in the "Recommendation Id" field
    When I copy the "Id" field
    When I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Recommendation has been Deleted!"
    Then the "Id" field should be empty
    And the "Name" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "NOT FOUND"

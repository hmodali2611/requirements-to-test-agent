@SHOP-101
Feature: Apply a promo code at checkout

  As a shopper I want to apply a promo code to my cart So that I pay the discounted price

  @SHOP-101-TC01 @P1 @functional @AC1
  Scenario: Verify: A valid, active promo code reduces the order total by its discount percentage
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC1
    And Observe the result
    Then A valid, active promo code reduces the order total by its discount percentage

  @SHOP-101-TC02 @P1 @functional @AC2
  Scenario: Verify: An expired promo code shows the message "This code has expired" and the total is unchanged
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC2
    And Observe the result
    Then An expired promo code shows the message "This code has expired" and the total is unchanged

  @SHOP-101-TC03 @P1 @negative @AC2
  Scenario: Negative: AC2 with invalid input or state
    Given Invalid, expired or unauthorized data from the test data set
    When Attempt the action in AC2 with invalid input or state
    And Observe the message and resulting state
    Then The system rejects it as specified: An expired promo code shows the message "This code has expired" and the total is unchanged

  @SHOP-101-TC04 @P1 @negative @AC4
  Scenario: Negative: AC4 with invalid input or state
    Given Invalid, expired or unauthorized data from the test data set
    When Attempt the action in AC4 with invalid input or state
    And Observe the message and resulting state
    Then The system rejects it as specified: Only one promo code can be applied per order

  @SHOP-101-TC05 @P2 @functional @AC3
  Scenario: Verify: Promo codes are case-insensitive
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC3
    And Observe the result
    Then Promo codes are case-insensitive

  @SHOP-101-TC06 @P2 @functional @AC4
  Scenario: Verify: Only one promo code can be applied per order
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC4
    And Observe the result
    Then Only one promo code can be applied per order

  @SHOP-101-TC07 @P2 @functional @AC5
  Scenario: Verify: The promo code field accepts at most 20 characters
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC5
    And Observe the result
    Then The promo code field accepts at most 20 characters

  @SHOP-101-TC08 @P2 @boundary @AC5
  Scenario: Boundary: AC5 at 20 and 21
    Given Data set up to reach the limit of 20
    When Enter or add exactly 20
    And Verify it is accepted
    And Enter or add 21
    And Verify it is rejected with the documented message
    Then 20 is accepted and 21 is rejected

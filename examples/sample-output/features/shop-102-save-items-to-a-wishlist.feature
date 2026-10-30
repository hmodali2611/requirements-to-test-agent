@SHOP-102
Feature: Save items to a wishlist

  As a signed-in shopper I want to save products to a wishlist So that I can buy them later

  @SHOP-102-TC01 @P1 @functional @AC1
  Scenario: Verify: Tapping the heart icon on a product adds it to the wishlist
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC1
    And Observe the result
    Then Tapping the heart icon on a product adds it to the wishlist

  @SHOP-102-TC02 @P1 @functional @AC2
  Scenario: Verify: A wishlist holds at most 50 items; adding a 51st shows "Wishlist is full"
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC2
    And Observe the result
    Then A wishlist holds at most 50 items; adding a 51st shows "Wishlist is full"

  @SHOP-102-TC03 @P1 @negative @AC2
  Scenario: Negative: AC2 with invalid input or state
    Given Invalid, expired or unauthorized data from the test data set
    When Attempt the action in AC2 with invalid input or state
    And Observe the message and resulting state
    Then The system rejects it as specified: A wishlist holds at most 50 items; adding a 51st shows "Wishlist is full"

  @SHOP-102-TC04 @P1 @negative @AC3
  Scenario: Negative: AC3 with invalid input or state
    Given Invalid, expired or unauthorized data from the test data set
    When Attempt the action in AC3 with invalid input or state
    And Observe the message and resulting state
    Then The system rejects it as specified: Guests who tap the heart icon are asked to sign in

  @SHOP-102-TC05 @P2 @boundary @AC2
  Scenario: Boundary: AC2 at 50 and 51
    Given Data set up to reach the limit of 50
    When Enter or add exactly 50
    And Verify it is accepted
    And Enter or add 51
    And Verify it is rejected with the documented message
    Then 50 is accepted and 51 is rejected

  @SHOP-102-TC06 @P2 @functional @AC3
  Scenario: Verify: Guests who tap the heart icon are asked to sign in
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC3
    And Observe the result
    Then Guests who tap the heart icon are asked to sign in

  @SHOP-102-TC07 @P2 @functional @AC4
  Scenario: Verify: The wishlist syncs between the iOS app, the Android app and the website
    Given Test user and data from the test data set
    When Open the feature under test
    And Perform the action described in AC4
    And Observe the result
    Then The wishlist syncs between the iOS app, the Android app and the website

  @SHOP-102-TC08 @P2 @cross_platform @AC4
  Scenario: Cross-platform: AC4 on iOS, Android and web
    Given Same account signed in on iOS, Android and web
    When Make the change on iOS
    And Refresh Android and web
    And Make a change on web
    And Refresh iOS and Android
    Then All three platforms show the same state within the sync window

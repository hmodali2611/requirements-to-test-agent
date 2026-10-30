# Story: SHOP-101 Apply a promo code at checkout

As a shopper
I want to apply a promo code to my cart
So that I pay the discounted price

## Acceptance criteria
- AC1: A valid, active promo code reduces the order total by its discount percentage
- AC2: An expired promo code shows the message "This code has expired" and the total is unchanged
- AC3: Promo codes are case-insensitive
- AC4: Only one promo code can be applied per order
- AC5: The promo code field accepts at most 20 characters

# Story: SHOP-102 Save items to a wishlist

As a signed-in shopper
I want to save products to a wishlist
So that I can buy them later

## Acceptance criteria
- AC1: Tapping the heart icon on a product adds it to the wishlist
- AC2: A wishlist holds at most 50 items; adding a 51st shows "Wishlist is full"
- AC3: Guests who tap the heart icon are asked to sign in
- AC4: The wishlist syncs between the iOS app, the Android app and the website

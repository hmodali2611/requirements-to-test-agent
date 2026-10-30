# Traceability matrix

## SHOP-101 Apply a promo code at checkout

LLM rounds: 2 · Tests: 8

| Criterion | Tests | Types |
| --- | --- | --- |
| AC1: A valid, active promo code reduces the order total by its discount percentage | SHOP-101-TC01 | functional |
| AC2: An expired promo code shows the message "This code has expired" and the total is unchanged | SHOP-101-TC02, SHOP-101-TC03 | functional, negative |
| AC3: Promo codes are case-insensitive | SHOP-101-TC05 | functional |
| AC4: Only one promo code can be applied per order | SHOP-101-TC04, SHOP-101-TC06 | functional, negative |
| AC5: The promo code field accepts at most 20 characters | SHOP-101-TC07, SHOP-101-TC08 | boundary, functional |

## SHOP-102 Save items to a wishlist

LLM rounds: 2 · Tests: 8

| Criterion | Tests | Types |
| --- | --- | --- |
| AC1: Tapping the heart icon on a product adds it to the wishlist | SHOP-102-TC01 | functional |
| AC2: A wishlist holds at most 50 items; adding a 51st shows "Wishlist is full" | SHOP-102-TC02, SHOP-102-TC03, SHOP-102-TC05 | boundary, functional, negative |
| AC3: Guests who tap the heart icon are asked to sign in | SHOP-102-TC04, SHOP-102-TC06 | functional, negative |
| AC4: The wishlist syncs between the iOS app, the Android app and the website | SHOP-102-TC07, SHOP-102-TC08 | cross_platform, functional |

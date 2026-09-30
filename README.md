Part A- SQL Task 5:
1. Why did you use INNER JOIN, LEFT JOIN, NOT EXISTS, or another approach?-  I used "join" and "left join". "Left join" keeps items from left table
   and returns NULL for non-matching rows in the right table. Filtered using "Where" gives only unmatched products.
2. What would change if product_id was not unique?- id product id is not unique, there might be confusion in results like duplicate records and mismatch in desired results.
3. What issue could happen if price or status can be NULL?- If Price or status are NULL, filtering or sorting of pricing and status will also give NULL.

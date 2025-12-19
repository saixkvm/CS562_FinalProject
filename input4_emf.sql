WITH t1 AS (
    SELECT cust, month, year, MIN(quant) as min_quant
    FROM sales
    GROUP BY cust, month, year
),
t2 AS (
    SELECT t1.cust, t1.month, t1.year, MIN(sales.quant) as min_quant
    FROM sales
	JOIN t1 ON sales.cust != t1.cust AND sales.month = t1.month and sales.year = t1.year
	GROUP BY t1.cust, t1.month, t1.year
),
t3 AS (
    SELECT t1.cust, t1.month, t1.year, MIN(sales.quant) as min_quant
    FROM sales
	JOIN t1 ON sales.cust = t1.cust AND sales.month != t1.month and sales.year = t1.year
	GROUP BY t1.cust, t1.month, t1.year
),
t4 AS (
    SELECT t1.cust, t1.month, t1.year, MIN(sales.quant) as min_quant
    FROM sales
	JOIN t1 ON sales.cust = t1.cust AND sales.month = t1.month and sales.year != t1.year
	GROUP BY t1.cust, t1.month, t1.year
)
SELECT t1.cust, 
       t1.month, 
       t1.year,
       t1.min_quant as current_min,
       t2.min_quant as other_customers_min,
       t3.min_quant as other_months_min,
       t4.min_quant as other_years_min
FROM t1
JOIN t2 ON t1.cust = t2.cust AND t1.month = t2.month AND t1.year = t2.year
JOIN t3 ON t1.cust = t3.cust AND t1.month = t3.month AND t1.year = t3.year
JOIN t4 ON t1.cust = t4.cust AND t1.month = t4.month AND t1.year = t4.year
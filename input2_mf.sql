with t1 as (
	SELECT cust, month, MAX(quant) as max_2017_quant
	FROM sales
	WHERE year = 2017
	GROUP BY cust, month
),
t2 as (
	SELECT cust, month, MAX(quant) as max_2018_quant
	FROM sales
	WHERE year = 2018
	GROUP BY cust, month
),
t3 as (
	SELECT cust, month, MAX(quant) as max_2019_quant
	FROM sales
	WHERE year = 2019
	GROUP BY cust, month
)
SELECT t1.cust, t1.month, t1.max_2017_quant, t2.max_2018_quant, t3.max_2019_quant
FROM t1
JOIN t2 ON t1.cust = t2.cust AND t1.month = t2.month AND t1.max_2017_quant > t2.max_2018_quant
JOIN t3 ON t1.cust = t3.cust AND t1.month = t3.month AND t1.max_2017_quant > t3.max_2019_quant
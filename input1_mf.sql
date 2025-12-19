with NJ as (
	SELECT cust, prod, SUM(quant) as nj_quant
	FROM sales
	WHERE state = 'NJ'
	GROUP BY cust, prod
),
NY as (
	SELECT cust, prod, SUM(quant) as ny_quant
	FROM sales
	WHERE state = 'NY'
	GROUP BY cust, prod
),
CT as (
	SELECT cust, prod, SUM(quant) as ct_quant
	FROM sales
	WHERE state = 'CT'
	GROUP BY cust, prod
)
SELECT NJ.cust, NJ.prod, NJ.nj_quant, NY.ny_quant, CT.ct_quant
FROM NJ
JOIN NY ON NJ.cust = NY.cust AND NJ.prod = NY.prod
JOIN CT ON NJ.cust = CT.cust AND NJ.prod = CT.prod
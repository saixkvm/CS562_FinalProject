WITH t1 AS (
    SELECT prod, month, year, AVG(quant) as avg_quant
    FROM sales
    GROUP BY prod, month, year
),
t2 AS (
    SELECT prod, year, AVG(quant) as avg_quant
    FROM sales
    GROUP BY prod, year
),
t3 AS (
    SELECT prod, month, year, AVG(quant) as avg_quant
    FROM sales
    WHERE state = 'NJ'
	GROUP BY prod, month, year
)
SELECT t1.prod, 
       t1.month, 
       t1.year,
       ROUND(t1.avg_quant, 3) as current_month_avg,
       ROUND(t2.avg_quant, 3) as year_avg,
	   --Some groups don't have the NJ column (guessing there weren't any purchases in NJ)
	   --Got it from here https://www.w3schools.com/sql/sql_isnull.asp
       ROUND(COALESCE(t3.avg_quant,0), 3) as nj_avg
FROM t1
LEFT JOIN t2 ON t1.prod = t2.prod AND t1.year = t2.year
LEFT JOIN t3 on t1.prod = t3.prod AND t1.month = t3.month AND t1.year = t3.year
with t1 as (
    SELECT year, COUNT(*) as butter_count, MAX(quant) as butter_max
    FROM sales
    WHERE prod = 'Butter'
    GROUP BY year
),
t2 as (
    SELECT year, COUNT(*) as jelly_count, MAX(quant) as jelly_max
    FROM sales
    WHERE prod = 'Jelly'
    GROUP BY year
),
t3 as (
    SELECT year, COUNT(*) as ham_count, MAX(quant) as ham_max
    FROM sales
    WHERE prod = 'Ham'
    GROUP BY year
),
t4 as (
    SELECT year, COUNT(*) as apple_count, MAx(quant) as apple_max
    FROM sales
    WHERE prod = 'Apple'
    GROUP BY year
)
SELECT t1.year, t1.butter_count, t1.butter_max,
        t2.jelly_count, t2.jelly_max,
        t3.ham_count, t3.ham_max,
        t4.apple_count, t4.apple_max
FROM t1
JOIN t2 ON t1.year = t2.year AND t1.butter_count > t2.jelly_count
JOIN t3 ON t1.year = t3.year
JOIN t4 ON t1.year = t4.year
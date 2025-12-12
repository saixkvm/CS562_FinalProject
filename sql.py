import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv


def query():
    """
    Used for testing standard queries in SQL.
    """
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("with p1 as (select cust,prod, sum(quant) as q1 from sales where sales. state = 'NJ' group by cust, prod),p2 as (select cust,prod, sum(quant) as q2 from sales where sales.state = 'NY' group by cust, prod), p3 as (select cust,prod,sum(quant) as q3 from sales where sales.state = 'CT' group by cust, prod) select p1.cust, p1.prod, p1.q1 as \"1_sum_quant\", p2.q2 as \"2_sum_quant\", p3.q3 as \"3_sum_quant\" from p1, p2, p3 where p1.cust = p2.cust and p2.cust = p3.cust and p1.cust = p3.cust and p1.prod = p2.prod and p2.prod = p3.prod and p1.prod = p3.prod")

    return tabulate.tabulate(cur.fetchall(),
                             headers="keys", tablefmt="psql")


def main():
    print(query())


if "__main__" == __name__:
    main()
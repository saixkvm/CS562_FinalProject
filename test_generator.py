from generator import main as generator
from _generated import query as _generated
from sql import query as sql


def test_generator():
    # Generate the file
    # generator()

    generated_result = _generated()
    sql_result = sql()
    
    print(generated_result)
    print(sql_result)
    # Sort both results by converting to sorted list of strings
    # This handles the fact that tabulate returns a string
    # gen_lines = sorted(generated_result.strip().split('\n'))
    # sql_lines = sorted(sql_result.strip().split('\n'))
    
    # assert gen_lines == sql_lines

test_generator()
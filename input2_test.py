from generator import main as generator
from input2_mf_generated import query as _generated
from sql import query as sql


def test_generator():
    # Generate the file

    # Sort both results by converting to sorted list of strings
    # This handles the fact that tabulate returns a string
    
    _generated_results = _generated()
    print("Done with getting _generated results!")
    sql_results = sql()
    print("Done with getting sql results!")
    
    #Remove the column_names and the seperators (i.e. "-----------")
    _generated_results = _generated_results.split("\n")[3:]
    _generated_results.pop()
    
    #Remove all of the space in all of the lines
    for i in range(len(_generated_results)):
        _generated_results[i] = _generated_results[i].replace(" ", "")
    
    
    #Same reasoning for _generated_results
    sql_results = sql_results.split("\n")[3:]
    sql_results.pop()
    for i in range(len(sql_results)):
        sql_results[i] = sql_results[i].replace(" ", "")

    assert sorted(_generated_results) == sorted(sql_results)
    print("Same!")
test_generator()
from generator import main as generator
from input5_emf_generated import query as _generated
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


    #Assert is going to failed because rounding the averages is different between python and postgres, but it outputs the same values
    #Here are the differences
    #https://www.diffchecker.com/3otSbwdH/
    #_generated: |Apple|9|2018|497.812|541.637|509.25|, sql: |Apple|9|2018|497.813|541.637|509.25|
    #_generated: |Cherry|2|2020|304.562|490.119|365|, sql: |Cherry|2|2020|304.563|490.119|365|
    #_generated: |Dates|1|2018|567.062|516.547|518.5|, sql: |Dates|1|2018|567.063|516.547|518.5|
    #_generated: |Dates|6|2019|567.812|486.505|575.2|, sql: |Dates|6|2019|567.813|486.505|575.2|
    #_generated: |Eggs|10|2020|451.062|526.063|361.5|, sql: |Eggs|10|2020|451.063|526.063|361.5|
    #_generated: |Eggs|2|2017|285.077|488.538|46.6667|, sql: |Eggs|2|2017|285.077|488.538|46.667|
    #_generated: |Fish|7|2016|431.562|474.971|523.8|, sql: |Fish|7|2016|431.563|474.971|523.8|
    #_generated: |Grapes|11|2020|621.312|504.609|331|, sql: |Grapes|11|2020|621.313|504.609|331|
    #_generated: |Grapes|3|2017|426.062|448.726|537|, sql: |Grapes|3|2017|426.063|448.726|537|
    #_generated: |Grapes|8|2017|580.062|448.726|517.25|, sql: |Grapes|8|2017|580.063|448.726|517.25|
    #_generated: |Ham|2|2019|409.812|507.812|339.5|, sql: |Ham|2|2019|409.813|507.812|339.5|
    #_generated: |Ice|12|2017|551.062|514.06|374|, sql: |Ice|12|2017|551.063|514.06|374| 
    #_generated: |Jelly|12|2020|499.562|521.746|583|, sql: |Jelly|12|2020|499.563|521.746|583|
    #_generated: |Jelly|8|2020|332.062|521.746|318|, sql: |Jelly|8|2020|332.063|521.746|318|
    assert sorted(_generated_results) == sorted(sql_results)
    print("Same!")
test_generator()#
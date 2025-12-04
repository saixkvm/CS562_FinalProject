def sql_syntax_to_python(s):
    s = s.replace("AND","and")
    s = s.replace("OR","or")
    s = s.replace("NOT","not")
    s = s.replace("=","==")
    
    

def do_predicate(predlistforgroupingvariable):
    predlistforgroupingvariable = sql_syntax_to_python(predlistforgroupingvariable)
    
    
    
    
    

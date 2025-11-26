def tokenize_expr(group, expr):
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}
    output_stack = []
    operator_stack = []
    
    c = 0
    last_token = None
    while c < len(expr):
        
        #Handles -3, -(3+4), (-3 + 4),  -1_sum_quant
        if expr[c] == "-" and (c == 0 or (last_token in "+-/*(")):
            output_stack.append("-1")
            operator_stack.append("*")
            c += 1
        
        if expr[c] == " ":
            c += 1
            continue
        
        #Parentheses
        elif expr[c] == "(":
            operator_stack.append(expr[c])
            last_token = "("
        
        elif expr[c] == ")":
            while operator_stack and operator_stack[-1] != "(":
                output_stack.append(operator_stack.pop())
            operator_stack.pop()
            last_token = ")"
        
        #Operator
        elif expr[c] in "+-/*":
            while operator_stack and operator_stack[-1] in precedence and precedence[operator_stack[-1]] >= precedence[expr[c]]:
                output_stack.append(operator_stack.pop())
            operator_stack.append(expr[c])
            last_token = expr[c]
            
        else:
            #Number or variable
            tmp = ""
            
            while c < len(expr) and expr[c] not in " +-/*()":
                tmp += expr[c]
                c += 1
            
            if not "_" in tmp: #Its a number
                output_stack.append(tmp)
            
            
            last_token = tmp
            continue
    
        c += 1
    
    while operator_stack:
        output_stack.append(operator_stack.pop())
    
    return output_stack


print(tokenize_expr([], "3 + 4 * 2 / ( 1 - 5 )") == ['3', '4', '2', '*', '1', '5', '-', '/', '+'])
print(tokenize_expr([], "-3 + 4") == ['-1', '3', '*', '4', '+'])
print(tokenize_expr([], "3 + -2 * 4") == ['3', '-1', '2', '*', '4', '*', '+'])
print(tokenize_expr([], "(3 + 4) * 5") == ['3', '4', '+', '5', '*'])
print(tokenize_expr([], "5 + ((1 + 2) * 4) - 3") == ['5', '1', '2', '+', '4', '*', '+', '3', '-'])
print(tokenize_expr([], "-(3 + 2) * 4") == ['-1', '3', '2', '+', '*', '4', '*'])
print(tokenize_expr([], "3 - 4 + 5") == ['3', '4', '-', '5', '+'])
print(tokenize_expr([], "-2 * -3") == ['-1', '2', '*', '-1', '3', '*', '*'])
print(tokenize_expr([], "((3))") == ['3'])

print(tokenize_expr([], "(3 + 4) * 5"))

import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv
def query():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []

    def input_processing():
        with open("input.txt", "r") as f:
            data = f.read()

        parts = data.split(":")
        
        # SELECT ATTRIBUTES LIST
        select_attributes = parts[1].split('\n')
        select_attributes.pop(0)
        select_attributes.pop(len(select_attributes)-1)
        select_attributes = select_attributes[0].split(',')
        for i in range(len(select_attributes)):
            select_attributes[i] = select_attributes[i].strip()

        # NUMBER OF GROUPING VARIABLES
        numberOfGroupingVariables = parts[2].split('\n')[1]
        # print(numberOfGroupingVariables)

        # GROUPING VARIABLES LIST
        groupingvariables = parts[3].split('\n')[1]
        groupingattributes = set(map(lambda x: x.strip(),groupingvariables.split(',')))

        # VECTOR OF AGGREGATE FUNCTIONS
        vectorOfAggregateFunctions = parts[4].split('\n')[1]
        vectorOfAggregateFunctions = vectorOfAggregateFunctions.split(',')
        for i in range(len(vectorOfAggregateFunctions)):
            vectorOfAggregateFunctions[i] = vectorOfAggregateFunctions[i].strip()

        # hset = set()
        # res = []
        # for i in range(len(vectorOfAggregateFunctions)):
        #     attr = vectorOfAggregateFunctions[i].split("_")[0]
        #     if attr not in hset:
        #         tmp = [vectorOfAggregateFunctions[i]]
        #         hset.add(attr)
        #         for j in range(i+1, len(vectorOfAggregateFunctions)):
        #             checkattr = vectorOfAggregateFunctions[j].split("_")[0]
        #             if checkattr == attr:
        #                 tmp.append(vectorOfAggregateFunctions[j])
        #         res.append(tmp)

        # vectorOfAggregateFunctions = res

        hset = {}
        for i in range(len(vectorOfAggregateFunctions)):
            attr_agg = vectorOfAggregateFunctions[i].split("_",1)
            attr, agg  = attr_agg[0], attr_agg[1]
            if attr not in hset:
                hset[attr] = [agg]
            else:
                if not agg in hset[attr]:
                    hset[attr].append(agg)

        vectorOfAggregateFunctions = hset

        # PREDICATE LIST
        predicateList = parts[5].split('\n')
        predicateList.pop(0)
        predicateList.pop(len(predicateList)-1)

        def predicate_list_splitting_by_ops(s):
            ops = [' AND ', ' OR ', ' NOT ']
            andsplitlist = s.split(ops[0]) # splitting by AND operator
            res = []
            for andsplit in andsplitlist:
                orsplitlist = andsplit.split(ops[1])
                for orsplit in orsplitlist:
                    notsplitlist = orsplit.split(ops[2])
                    for notsplit in notsplitlist:
                        res.append(notsplit)
            for r in range(len(res)):
                res[r] = res[r].strip()
            return res

        def predicate_list_splitting_by_types(s):
            types = ['>=', '<=', "!=", '=', '>', "<"]

            reslist = []
            for t in types:
                if t in s:
                    reslist = s.split(t)
                    break 
            tmp = reslist[0].split('.')
            tmp2 = reslist[1]
            reslist = []
            for i in range(len(tmp)):
                reslist.append(tmp[i])
            reslist.append(tmp2)
            return reslist

        predicatehashmap = {}
        # for p in predicateList:
        #     tmplist = predicate_list_splitting_by_ops(p)
        #     for t in tmplist:
        #         condition = t.split(".")
        #         if condition[0] in predicatehashmap:
        #             predicatehashmap[condition[0]].append(condition[1])
        #         else:
        #             predicatehashmap[condition[0]] = [condition[1]]  
        for p in predicateList:
            #tmplist = predicate_list_splitting_by_ops(p)
            cond = p.split(".")
            predicatehashmap[cond[0]] = p


        # HAVING CLAUSE
        # In case there are aggregates in the having clause but not in the vectorOfAggregateFunctions
        havingClause = ""
        if parts[6].strip() != "" and parts[6].strip().upper() != "NONE":
            havingClause = parts[6].split('\n')[1]

            c = 0
            while c < len(havingClause):
                if havingClause[c] in " =*><!()/+-":
                    c += 1
                    continue
            
                tmp = ""        
                while c < len(havingClause) and havingClause[c] not in " =*><!()/+-":
                    tmp += havingClause[c]
                    c += 1
            
                if "_" in tmp:
                    group_variable, agg_func = tmp.split("_",1)
                    if agg_func not in vectorOfAggregateFunctions[group_variable]:
                        vectorOfAggregateFunctions[group_variable].append(agg_func)


        print(select_attributes)
        print(numberOfGroupingVariables)
        print(groupingattributes)
        print(vectorOfAggregateFunctions)
        print(predicatehashmap)
        print(havingClause)

        return [select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause]

    def aggrfunctioncompute(s):
        return s.split("_")

    def get_agg_idx(gV, agg_func):
        for idx, agg in enumerate(vectorOfAggregateFunctions[gV]):
            if agg == agg_func:
                return idx
            
            
    # def has_grouping_variables(group, gVs):
    #     for gv in gVs
    #     return True
    
    
    def get_col_op_value(cond):
        res = cond.split('.')
        tmp = res[1]
        operator = ''
        for op in ["!=", ">=", "<=", ">", "<", "="]:
            if op in tmp:
                operator = op
                break 
        tmp = tmp.split(operator)
        col = tmp[0].strip()
        val = tmp[1].strip()

        
        if val.isdigit():
            val = int(val)

        if isinstance(val, str):
            val = val.strip("'")
        return [col, operator, val]

    def get_expr_value(cond):
        operator = ''
        for op in ["!=", ">=", "<=", ">", "<", "="]:
            if op in cond:
                operator = op
                break 
        tmp = cond.split(operator)
        expr1 = tmp[0]
        expr2 = tmp[1]

        if isinstance(expr1, str):
            expr1 = expr1.strip("'")

        if isinstance(expr2, str):
            expr2 = expr2.strip("'")
            
        return [expr1, operator, expr2]
    
    
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
                
                else: #Its a variable
                    group_variable, agg_func = tmp.split("_",1)
                    idx = get_agg_idx(group_variable, agg_func)
                    num = mfstructdict[group][group_variable][idx]
                    if isinstance(num, list): #AVG
                        num = num[2]
                    output_stack.append(str(num))
                
                last_token = tmp
                continue
        
            c += 1
        
        while operator_stack:
            output_stack.append(operator_stack.pop())
        
        return output_stack
    
    def eval_expr(group, expr):
        #Reverse Polish Notation
        #Shoutout Leetcode 150
        tokens = tokenize_expr(group, expr)
        stack = []
        
        for token in tokens:
            if token in "+-/*":
                b = float(stack.pop())
                a = float(stack.pop())
                
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    stack.append(a / b)
            else:
                stack.append(token)
        
        return float(stack[0])
    
    def eval_having(group, cond):
        final_bool = True
        
        [expr1, op, expr2] = get_expr_value(cond)
        match op:
            case "!=":
                final_bool = eval_expr(group, expr1) != eval_expr(group, expr2)
            case ">=":
                final_bool = eval_expr(group, expr1) >= eval_expr(group, expr2)
            case "<=":
                final_bool = eval_expr(group, expr1) <= eval_expr(group, expr2)
            case ">":
                final_bool = eval_expr(group, expr1) > eval_expr(group, expr2)
            case "<":
                final_bool = eval_expr(group, expr1) < eval_expr(group, expr2)
            case "=":
                final_bool = eval_expr(group, expr1) == eval_expr(group, expr2)
            case _:
                print(f"Unknonw op: {op}")
        
        
        return final_bool
    
    def eval_predicate(row, cond):
        final_bool = True
        [col, op, val] = get_col_op_value(cond)
        
        match op:
            case "!=":
                final_bool = row[col] != val
            case ">=":
                final_bool = row[col] >= val
            case "<=":
                final_bool = row[col] <= val
            case ">":
                final_bool = row[col] > val
            case "<":
                final_bool = row[col] < val
            case "=":
                final_bool = row[col] == val
            case _:
                print(f"Unknown op: {op}")
        
        return final_bool

    
    def eval_not_cond(row, cond, fn):
        not_flag = False

        
        if cond.upper().strip().startswith("NOT "):
            not_flag = True
            cond = cond.strip()[4:].strip()
        
        result = fn(row,cond)
        return not result if not_flag else result

    def evalandcond(row, cond, fn):
        evalconds = cond.split(' AND ')
        finalbool = True 

        for cond in evalconds:
            finalbool = finalbool and eval_not_cond(row, cond, fn)
        return finalbool

    def evaluateConditions(row, predlistforgroupingvariable, fn):
        # split by OR'S
        evalconds = predlistforgroupingvariable.split(' OR ')
        finalbool = False
        for cond in evalconds:
            # cond can contain ANDS now
            finalbool = finalbool or evalandcond(row, cond, fn)
        return finalbool
    
    select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause = input_processing()

    '''
    key: specific group value -> 
        {
            attr_1: attr_1 value
            ...
            attr_n : attr_n value
            grouping variable -> [list of aggr funcs respective to that gv]
        }
    '''
    # THIS PASS IS FOR CREATING THE MF STRUCT
    mfstructdict = {}
    for row in cur:
        # Create the key for MFStruct - Represents the value for each unique combo of attributes
        groupingattributekey = tuple(row[attr] for attr in groupingattributes)

        # If our key is not in MFStruct
        if groupingattributekey not in mfstructdict:

            # We create a new map
            aggrfuncmap = {}

            # We first populate it with the values of group attributes
            # such as cust = 'Jake"
            for attr in groupingattributes:
                aggrfuncmap[attr] = row[attr]

            # For each grouping variable we map it to a list of aggregate functions
            for key in vectorOfAggregateFunctions:
                aggrfuncmap[key] = [0] * len(vectorOfAggregateFunctions[key])
                for key2 in range(0,len(vectorOfAggregateFunctions[key])):
                    tmp = aggrfunctioncompute(vectorOfAggregateFunctions[key][key2])
                    if tmp[0] == "min":
                        aggrfuncmap[key][key2] = float('inf')
                    if tmp[0] == 'max':
                        aggrfuncmap[key][key2] = float('-inf')
                    if tmp[0] == 'avg':
                        # [Total Sum, Count, Avg]
                        aggrfuncmap[key][key2] = [0,0,0]
                    
            mfstructdict[groupingattributekey] = aggrfuncmap

    for key in vectorOfAggregateFunctions:
        # the predicate list for that grouping variable
        predlistforgroupingvariable = predicatehashmap[key]
        cur.execute("SELECT * FROM sales")
        for row in cur:  
            #UPDATE THE MFSTRUCTDICT
            #update the grouping variables aggr funcs
            for groupingattributekey in mfstructdict:
                
                rowchecktuple = tuple(row[attr] for attr in groupingattributes)
                
                if rowchecktuple == groupingattributekey:
                    if evaluateConditions(row, predlistforgroupingvariable, eval_predicate):
                        # the aggregate functions from that grouping variable
                        aggrfuncs = vectorOfAggregateFunctions[key]
                        for index in range(len(aggrfuncs)):
                            function, attribute = aggrfunctioncompute(aggrfuncs[index])
                            # min, max, avg, sum, count
                            if function == "count":
                                mfstructdict[groupingattributekey][key][index] +=1
                            elif function == "sum":
                                mfstructdict[groupingattributekey][key][index] += row[attribute]
                            elif function == "min":
                                mfstructdict[groupingattributekey][key][index] = min(mfstructdict[groupingattributekey][key][index], row[attribute])
                            elif function == "max":
                                mfstructdict[groupingattributekey][key][index] = max(mfstructdict[groupingattributekey][key][index], row[attribute])
                            else:
                                num, denom, avg = mfstructdict[groupingattributekey][key][index]
                                num += row[attribute]
                                denom += 1
                                avg = num/denom
                                mfstructdict[groupingattributekey][key][index] = [num, denom, avg]
                    

    #HAVING CLAUSE
    if havingClause != "":
        for key in vectorOfAggregateFunctions:
              for groupingattributekey in list(mfstructdict.keys()):
                  if not evaluateConditions(groupingattributekey, havingClause, eval_having):
                      del mfstructdict[groupingattributekey]
                      
                      
                      
    for grouping_key, aggrfuncmap in mfstructdict.items():
        row = {}
        
        for attr in select_attributes:
            if attr in groupingattributes:
                row[attr] = aggrfuncmap[attr]
            else:
                
                gV, agg = attr.split("_",1)
                idx = get_agg_idx(gV, agg)
                if isinstance(mfstructdict[grouping_key][gV][idx], list): #AVG
                    row[attr] = mfstructdict[grouping_key][gV][idx][2]
                else:
                    
                    row[attr] = mfstructdict[grouping_key][gV][idx]
        _global.append(row)
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
        
if "__main__" == __name__:
    main()

    
    
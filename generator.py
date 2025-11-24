import subprocess

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
    groupingattributes = list(map(lambda x: x.strip(),groupingvariables.split(',')))

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
    for p in predicateList:
        tmplist = predicate_list_splitting_by_ops(p)
        for t in tmplist:
            condition = t.split(".")
            if condition[0] in predicatehashmap:
                predicatehashmap[condition[0]].append(condition[1])
            else:
                predicatehashmap[condition[0]] = [condition[1]]  


    # HAVING CLAUSE
    havingClause = parts[6].split('\n')[1]

    # print(select_attributes)
    # print(numberOfGroupingVariables)
    # print(groupingattributes)
    # print(vectorOfAggregateFunctions)
    # print(predicatehashmap)
    # print(havingClause)

    return [select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause]

def aggrfunctioncompute(s):
    return s.split("_")

def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause = input_processing()

    mfstructdict = {}

    if len(groupingattributes) == 1:

        # Filling up the MFSTRUCT-Dictionary
        '''
        key: specific group value -> 
            {
                grouping variable -> [list of aggr funcs respective to that gv]
            }
        '''
        for row in cur:
            if row[groupingattributes[0]] not in mfstructdict:

                aggrfuncmap = {}
                for key in vectorOfAggregateFunctions:
                    aggrfuncmap[key] = [0] * len(vectorOfAggregateFunctions[key])
                    for key2 in range(0,len(vectorOfAggregateFunctions[key])):
                        tmp = aggrfunctioncompute(vectorOfAggregateFunctions[key][key2])
                        if tmp[0] == "min":
                            aggrfuncmap[key][key2] = float('inf')
                        if tmp[0] == 'max':
                                aggrfuncmap[key][key2] = float('-inf')



        index = 0
        for scan in range(0, len(vectorOfAggregateFunctions)):
            aggrfuncs = vectorOfAggregateFunctions[scan]
            for key in mfstructdict:
                scan_predicate = predicateList[scan]
                groupingvar, attrtocheck, condition, typetoadd = predicate_list_splitting_by_types(scan_predicate)

                count = 1
                cur.execute("SELECT * FROM sales")
                for row in cur:
                    if key == row[groupingattributes[0]]:
                        if typetoadd == ">":
                            if row[attrtocheck] > condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                        elif typetoadd == ">=":
                            if row[attrtocheck] >= condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                        elif typetoadd == "=":
                            if row[attrtocheck] == condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                        elif typetoadd == "<=":
                            if row[attrtocheck] <= condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                        elif typetoadd == "<":
                            if row[attrtocheck] < condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                        else:
                            if row[attrtocheck] != condition:
                                reset = index
                                for s in aggrfuncs:
                                    gv, af, a = aggrfunctioncompute(s)
                                    if af == "sum":
                                        mfstructdict[key][index] += row[a]
                                    elif af == "min":
                                        mfstructdict[key][index] = min(mfstructdict[key][index],row[a])
                                    elif af == "max":
                                        mfstructdict[key][index] = max(mfstructdict[key][index],row[a])
                                    elif af == "count":
                                        mfstructdict[key][index] +=1
                                    else:
                                         mfstructdict[key][index] =  (mfstructdict[key][index] + row[a])/count 
                                         count+=1
                                    index+=1
                                index = reset
                index += len(aggrfuncs)
    # else:
    #     for row in cur:
    #         tmp = []
    #         for attr in groupingattributes:
    #             tmp.append(row[attr])
    #         key = tuple(tmp)
    #         if key not in mfstructdict:
    #             mfstructdict[key] = [0] * len(vectorOfAggregateFunctions)
                

    # for scan in range(0, len(vectorOfAggregateFunctions)):
    #     for key in mfstructdict:
            
    body = """
    for row in cur:
        if row['quant'] >= 1000:
            _global.append(row)
    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()

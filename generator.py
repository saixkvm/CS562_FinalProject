import subprocess
import re
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


        predicatehashmap = {}

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


def create_gV_keys(vectorOfAggregateFunctions):
    res = ""
    for gV in vectorOfAggregateFunctions:
        for aggr in vectorOfAggregateFunctions[gV]:
            func = aggr.split("_")[0]
            full_func = gV + "_" + aggr
            if func == "min":
                res += f"        mfstruct[current_group]['{full_func}'] = float('inf')\n"
            elif func == "max":
                res += f"        mfstruct[current_group]['{full_func}'] = float('-inf')\n"
            elif func == "avg":
                res += f"        mfstruct[current_group]['{full_func}'] = [0,0,0]\n"
            else:
                res += f"        mfstruct[current_group]['{full_func}'] = 0\n"
    return res

def create_predicates(predicatehashmap, vectorOfAggregateFunctions):
    res = ""
    for gV, pred in predicatehashmap.items():
        pred = re.sub(r"\bAND\b", "and", pred)
        pred = re.sub(r"\bOR\b", "or", pred)
        pred = re.sub(r"\bNOT\b", "not", pred)
        pred = re.sub(r"(?<![<>!])=", "==", pred)
        pred = re.sub(r"\d+\.(\w*)",r"row['\1']",pred)
        
        res += f"                if {pred}:\n"
        
        for aggr in vectorOfAggregateFunctions[gV]:
            func, attribute = aggr.split("_")
            full_func = gV + "_" + aggr
            if func == "min":
                res += f"                    mfstruct[groupingattributekey]['{full_func}'] = min(mfstruct[groupingattributekey]['{full_func}'], row['{attribute}'])\n"
            elif func == "max":
                res += f"                    mfstruct[groupingattributekey]['{full_func}'] = max(mfstruct[groupingattributekey]['{full_func}'], row['{attribute}'])\n"
            elif func == "sum":
                res += f"                    mfstruct[groupingattributekey]['{full_func}'] += row['{attribute}']\n"
            elif func == "count":
                res += f"                    mfstruct[groupingattributekey]['{full_func}'] += 1\n"
            else:
                res += f"                    num, denom, avg = mfstruct[groupingattributekey]['{full_func}']\n"
                res += f"                    num += row['{attribute}']\n"
                res += f"                    denom += 1\n"
                res += f"                    avg = num/denom\n"
                res += f"                    mfstruct[groupingattributekey]['{full_func}'] = [num, denom, avg]\n"
    
    return res


def create_having(havingClause):
    res = ""
    if havingClause != "":
        havingClause = re.sub(r"\bAND\b", "and", havingClause)
        havingClause = re.sub(r"\bOR\b", "or", havingClause)
        havingClause = re.sub(r"\bNOT\b", "not", havingClause) 
        havingClause = re.sub(r"(?<![<>!])=", "==", havingClause)
        havingClause = re.sub(r"(\w+_(?:sum|avg|min|max)_\w+)", r"mfstruct['groupingattributekey']['\1']", havingClause)
        
        res += "    for groupingattributekey in mfstruct:\n"
        res += f"        if not ({havingClause}):\n"
        res += "            del mfstruct[groupingattributekey]"
    return res


def create_projection(select_attributes, groupingattributes):
    res = ""
    
    for attr in select_attributes:
        if attr in groupingattributes:
            res += f"row['{attr}'] = aggrfuncmap['{attr}']"
    return res

def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause = input_processing()
    
    body = f"""
    mfstruct = {{}}
    group = {tuple([gA for gA in groupingattributes])}
    
    #Creating the mfstruct
    for row in cur:
        current_group = tuple([row[attr] for attr in group])
        mfstruct[current_group] = dict()
        for attr in group:
            mfstruct[current_group][attr] = row[attr]
{create_gV_keys(vectorOfAggregateFunctions)}
    

    #Predicates
    cur.execute("SELECT * FROM sales")
    for row in cur:
        for groupingattributekey in mfstruct:
            rowchecktuple = tuple(row[attr] for attr in group)
            
            if rowchecktuple == groupingattributekey:
{create_predicates(predicatehashmap, vectorOfAggregateFunctions)}    



    #Having clause
{create_having(havingClause)}


    #Projection
    for groupingattributekey, aggrfuncmap in mfstruct.items():
        row = dict()
        
{create_projection(select_attributes, groupingattributes)}
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
    
    print(mfstruct)
    return 1
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """
    print(tmp)
    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    # subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()

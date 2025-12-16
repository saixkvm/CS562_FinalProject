import subprocess
import re
def input_processing():
        with open("input3.txt", "r") as f:
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
        numberOfGroupingVariables = int(parts[2].split('\n')[1])
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

        vector_keys = set(vectorOfAggregateFunctions.keys())
        predicate_keys = set(predicatehashmap.keys())
        all_keys = vector_keys | predicate_keys
        
        for attr in select_attributes:
            if not attr in groupingattributes and not attr in all_keys:
                raise ValueError(f"attr {attr} must appear in the grouping attributes list or be used in an aggregate function")
            
        if numberOfGroupingVariables != len(vector_keys) and numberOfGroupingVariables != len(predicate_keys):
            raise ValueError("Number of grouping variables doesn't match the number of grouping variables for the aggregate functions or predicates")
        
        return [select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause]


def create_gV_keys(vectorOfAggregateFunctions):
    res = ""
    for gV in vectorOfAggregateFunctions:
        for aggr in vectorOfAggregateFunctions[gV]:
            func = aggr.split("_")[0]
            full_func = gV + "_" + aggr
            match func:
                case "min":
                    res += f"        mfstruct[current_group]['{full_func}'] = float('inf')\n"
                case "max":
                    res += f"        mfstruct[current_group]['{full_func}'] = float('-inf')\n"
                case  "avg":
                    res += f"        mfstruct[current_group]['{full_func}'] = [0,0,0]\n"
                case "count" | "sum":
                    res += f"        mfstruct[current_group]['{full_func}'] = 0\n"
                case _:
                    raise ValueError("Unknown aggregate function")
    return res


def create_predicates(predicatehashmap, vectorOfAggregateFunctions):
    res = ""
    for gV, aggrs in vectorOfAggregateFunctions.items():
        res += f"               #Grouping variable {gV}\n"

        if gV in predicatehashmap:
            
            pred = predicatehashmap[gV]
            pred = re.sub(r"\bAND\b", "and", pred)
            pred = re.sub(r"\bOR\b", "or", pred)
            pred = re.sub(r"\bNOT\b", "not", pred)
            pred = re.sub(r"(?<![<>!])=", "==", pred)
            pred = pred.strip()
            
            
            condition_matches = re.findall(r"\d+\.(\w+)\s*([<>!=]+)\s*(?:'([^']*)'|(\w+))", pred)
            
            emf = False
            
            for condition in condition_matches:
                val1 = condition[0]
                op = condition[1]
                val2 = condition[2]
                val3 = condition[3]
                
                if val3 is None:
                    pred = re.sub(rf"\d+\.{val1}\s*{op}\s*{val2}", f"row['{val1}'] {op} {val2}", pred)
                elif val1 == val3:
                    emf = True
                    pred = re.sub(rf"\d+\.{val1}\s*{op}\s*{val3}", f"mfstruct[groupingattributekey]['{val1}'] {op} row['{val3}']",pred)
                else:
                    pred = re.sub(rf"\d+\.{val1}\s*{op}\s*{val3}", f"row['{val1}'] {op} {val3}", pred) 
            
            if emf:
                res += f"               if {pred}:\n"
            else:
                res += f"               if rowchecktuple == groupingattributekey and ({pred}):\n"
        else:
            res += f"                   if rowchecktuple == groupingattributekey:\n"
        for aggr in aggrs:
            func, attribute = aggr.split("_")
            full_func = gV + "_" + aggr
            if func == "min":
                res += f"                   mfstruct[groupingattributekey]['{full_func}'] = min(mfstruct[groupingattributekey]['{full_func}'], row['{attribute}'])\n"
            elif func == "max":
                res += f"                   mfstruct[groupingattributekey]['{full_func}'] = max(mfstruct[groupingattributekey]['{full_func}'], row['{attribute}'])\n"
            elif func == "sum":
                res += f"                   mfstruct[groupingattributekey]['{full_func}'] += row['{attribute}']\n"
            elif func == "count":
                res += f"                   mfstruct[groupingattributekey]['{full_func}'] += 1\n"
            else:
                res += f"                   num, denom, avg = mfstruct[groupingattributekey]['{full_func}']\n"
                res += f"                   num += row['{attribute}']\n"
                res += f"                   denom += 1\n"
                res += f"                   avg = num/denom\n"
                res += f"                   mfstruct[groupingattributekey]['{full_func}'] = [num, denom, avg]\n"
    
    return res


def create_having(havingClause):
    res = ""
    if havingClause != "":
        havingClause = re.sub(r"\bAND\b", "and", havingClause)
        havingClause = re.sub(r"\bOR\b", "or", havingClause)
        havingClause = re.sub(r"\bNOT\b", "not", havingClause) 
        havingClause = re.sub(r"(?<![<>!])=", "==", havingClause)
        havingClause = re.sub(r"(\w+_(?:sum|avg|min|max)_\w+)", r"mfstruct[groupingattributekey]['\1']", havingClause)
        
        res += "    try:\n"
        res += "        for groupingattributekey in list(mfstruct):\n"
        res += f"            if not ({havingClause}):\n"
        res += "                del mfstruct[groupingattributekey]\n"
        res += "    except KeyError:\n"
        res += "        raise ValueError('The having clause references an unknown attribute')"
    return res


def create_projection(select_attributes, groupingattributes):
    res = ""
    
    for attr in select_attributes:
        if attr in groupingattributes:
            res += f"        row['{attr}'] = aggrfuncmap['{attr}']\n"
        else:
            tmp = attr
            attr = re.sub(r"(\w+_(?:sum|min|max)_\w+)", r"aggrfuncmap['\1']", attr)
            attr = re.sub(r"(\w+_(?:avg)_\w+)", r"aggrfuncmap['\1'][2]", attr)
            res += f"        row['{tmp}'] = {attr}\n"
    return res

def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause = input_processing()
    
    body = f"""
    column_names = [desc[0] for desc in cur.description]
    
    mfstruct = {{}}
    group = {tuple([gA for gA in groupingattributes])}
    
    for column in group:
        if column not in column_names:
            raise ValueError("Unknown Column")
    #Creating the mfstruct
    for row in cur:
        current_group = tuple([row[attr] for attr in group])
        mfstruct[current_group] = dict()
        for attr in group:
            mfstruct[current_group][attr] = row[attr]
{create_gV_keys(vectorOfAggregateFunctions)}
    

    #Predicates
    #We just check the groups if the grouping variable doesn't have a predicate
    cur.execute("SELECT * FROM sales")
    for row in cur:
        rowchecktuple = tuple(row[attr] for attr in group)
        for groupingattributekey in mfstruct:
            try:
{create_predicates(predicatehashmap, vectorOfAggregateFunctions)} 
            except KeyError:
                raise ValueError("A grouping variable has an unknown column")



    #Having clause
{create_having(havingClause)}


    #Projection
    for groupingattributekey, aggrfuncmap in mfstruct.items():
        row = dict()
        
{create_projection(select_attributes, groupingattributes)}
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
    
    # print(mfstruct)
    # return 1
    # print(mfstruct[(11,'Grapes')])
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

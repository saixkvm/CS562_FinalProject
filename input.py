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

    aggrs = re.findall(r"(\w+_(?:sum|avg|min|max|count)_\w+)", havingClause)
    for aggr in aggrs:
        group_variable, aggr_func = aggr.split("_",1)
        if aggr_func not in vectorOfAggregateFunctions[group_variable]:
            vectorOfAggregateFunctions[group_variable].append(aggr_func)


print("Select Attributes", select_attributes)
print("Number of grouping variables", numberOfGroupingVariables)
print("Grouping Attributes", groupingattributes)
print("Vector of Agg Functions", vectorOfAggregateFunctions)
print("Predicate hashmap", predicatehashmap)
print("Having clause", havingClause)

vector_keys = set(vectorOfAggregateFunctions.keys())
predicate_keys = set(predicatehashmap.keys())
all_keys = vector_keys | predicate_keys

for attr in select_attributes:
    if "+" in attr or "-" in attr or "*" in attr or "/" in attr or "_" in attr:
        continue
    if not attr in groupingattributes and not attr in all_keys:
        raise ValueError(f"attr {attr} must appear in the grouping attributes list or be used in an aggregate function")
    
if numberOfGroupingVariables != len(vector_keys) and numberOfGroupingVariables != len(predicate_keys):
    raise ValueError("Number of grouping variables doesn't match the number of grouping variables for the aggregate functions or predicates")


# return [select_attributes, numberOfGroupingVariables, groupingattributes, vectorOfAggregateFunctions, predicatehashmap, havingClause]
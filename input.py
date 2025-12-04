with open("input.txt", "r") as f:
    data = f.read()

parts = data.split(":")
for part in parts:
    print(repr(part))
# SELECT ATTRIBUTES LIST
select_attributes = parts[1].split('\n')
select_attributes.pop(0)
select_attributes.pop(len(select_attributes)-1)
select_attributes = set(map(lambda x: x.strip(),select_attributes[0].split(',')))
# select_attributes = select_attributes[0].split(',')
# for i in range(len(select_attributes)):
#     select_attributes[i] = select_attributes[i].strip()

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
    #tmplist = predicate_list_splitting_by_ops(p)
    cond = p.split(".")
    predicatehashmap[cond[0]] = p
    # for t in tmplist:
    #     condition = t.split(".")
    #     if condition[0] in predicatehashmap:
    #         predicatehashmap[condition[0]].append(condition[1])
    #     else:
    #         predicatehashmap[condition[0]] = [condition[1]]  


# HAVING CLAUSE
havingClause = None
if parts[6].strip() != "" or parts[6].strip().upper() != "NONE":
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
        
print("Select attributes", select_attributes)
print("Number", numberOfGroupingVariables)
print("Grouping attributes", groupingattributes)
print("vector of agg funcs", vectorOfAggregateFunctions)
print("pred hashmap", predicatehashmap)
print(havingClause)
def aggrfunctioncompute(s):
    return s.split("_")



aggrfuncmap = {}
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

print(aggrfuncmap)
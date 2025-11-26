# 
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

hset = {}
for i in range(len(vectorOfAggregateFunctions)):
    attr_agg = vectorOfAggregateFunctions[i].split("_",1)
    attr, agg  = attr_agg[0], attr_agg[1]
    if attr not in hset:
        hset[attr] = [agg]
    else:
        hset[attr].append(agg)

vectorOfAggregateFunctions = hset
'''
GROUPING ATTRIBUTES LIST
['cust']

VECTOR OF AGGREGATE FUNCTIONS
'1': ['min_quant'], 
'3': ['avg_quant', 'sum_quant'], 
'2': ['sum_quant']


PRECIATE HASHMAP
'1': ["state='NY'"], 
'2': ["state='NJ'"], 
'3': ["state='CT'"]

HAVING CLAUSE
1_sum_quant > 2 * 2_sum_quant or 1_avg_quant > 3_avg_quant

'1': [inf], 
'3': [[0, 0, 0], 0], 
'2': [0]
    '''
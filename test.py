import re

def test(havingClause):
    havingClause = re.sub(r"\bAND\b", "and", havingClause)
    havingClause = re.sub(r"\bOR\b", "or", havingClause)
    havingClause = re.sub(r"\bNOT\b", "not", havingClause) 
    havingClause = re.sub(r"(?<![<>!])=", "==", havingClause)
    havingClause = re.sub(r"(\w+_(?:sum|avg|min)_\w+)", r"mfstruct['groupingattributekey']['\1']", havingClause)
    return havingClause
    
print(test("1_sum_quant>2 * 2_sum_quant or 1_avg_quant > 3_avg_quant"))
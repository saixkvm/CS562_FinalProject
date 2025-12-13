import re

# # List of test strings with different operators
# test_cases = [
#     "1.month = month",
#     "1.age > 18",
#     "1.salary < 5000",
#     "1.date <= startDate",
#     "1.score >= 90",
#     "1.status != active"
# ]

# # # Regex breakdown:
# # # \d+\.         -> Matches "1."
# # # (\w+)         -> Group 1: The variable name
# # # \s* -> Optional whitespace
# # # (?:...|...)   -> Non-capturing group for operators
# # #   <=|>=|!=    -> Matches multi-char operators first
# # #   |           -> OR
# # #   [=:<>]      -> Matches single-char operators
# # # \s* -> Optional whitespace
# # # (\w+)         -> Group 2: The value/variable
# pattern = r"\d+\.(\w+)\s*(?:<=|=|!=|[=<>])\s*(\w+)"

# # print(f"{'Input String':<25} | {'Group 1':<10} | {'Group 2'}")
# # print("-" * 50)

# # for text in test_cases:
# #     match = re.search(pattern, text)
# #     if match:
# #         if match.group(1).lower() == match.group(2).lower():
# #             text = f"mfstruct[groupingattributekey]['{match.group(1).lower()}'] == row['{match.group(1).lower()}']"
# #         else:
# #             text = f"row['{match.group(1).lower()}'] == {match.group(2).lower()}"
# #         print(text)
# #         # print(f"{text:<25} | {match.group(1):<10} | {match.group(2)}")
# pred = " and ".join(test_cases)
# pattern = r"\d+\.(\w+)\s*(?:<=|=|!=|[=<>])\s*(\w+)"
# match = re.findall(pattern,pred)
# print(match)



# import re

# def transform_query_to_python(query_str):
#     # 1. Define the Regex
#     # Captures:
#     # Group 1: The key after '1.' (value1)
#     # Group 2: The operator (=, <=, >=, !=, <, >)
#     # Group 3: The value (value2) - handles quoted strings OR raw numbers/variables
#     pattern = r"\d+\.(\w+)\s*(=|<=|>=|!=|<|>)\s*(?:'([^']*)'|(\w+))"

#     # 2. Define the callback function for re.sub
#     def replacement_logic(match):
#         val1 = match.group(1)      # e.g., 'state' or 'month'
#         operator = match.group(2)  # e.g., '=' or '>'
        
#         # Determine val2 and whether it was originally quoted
#         val2_quoted = match.group(3) # The content inside quotes (e.g., NJ)
#         val2_raw = match.group(4)    # The raw content (e.g., month, 100)
        
#         # Normalize operator for Python (convert single = to ==)
#         py_op = '==' if operator == '=' else operator

#         # --- LOGIC IMPLEMENTATION ---
        
#         # Check Rule 1: value1 == value2 (Comparing key vs raw variable name)
#         # We only check this if val2 was NOT quoted (i.e., val2_raw exists)
#         if val2_raw and val1 == val2_raw:
#             # Rule: mfstruct[groupingattributekey][<value1>] <operator> row[<value2>]
#             return f"mfstruct[groupingattributekey]['{val1}'] {py_op} row['{val2_raw}']"
        
#         else:
#             # Rule 2: else row['<value1>'] <operator> '<value2>'
            
#             # If val2 was originally quoted, keep it quoted in the output
#             if val2_quoted is not None:
#                 final_val2 = f"'{val2_quoted}'"
#             else:
#                 # If it was a number/variable, leave it raw (or quote it if you prefer strict strings)
#                 final_val2 = val2_raw

#             return f"row['{val1}'] {py_op} {final_val2}"

#     # 3. Perform the substitution
#     # flags=re.IGNORECASE handles 'AND'/'OR' casing if needed, though this regex ignores them
#     transformed_str = re.sub(pattern, replacement_logic, query_str)
    
#     return transformed_str

# # --- Test ---
# input_string = "14.state = 'NJ' and 1.month = month or 1.quant > 100"
# result = transform_query_to_python(input_string)

# print("Original:", input_string)
# print("Transformed:", result)

# input_string = "1.state = 'NJ' and 1.month = month or 1.quant > 100 or 2.quant >= 500" 

# pattern = r"\d+\.(\w+)\s*([<>!=]+)\s*(?:'([^']*)'|(\w+))"

# matches = re.findall(pattern, input_string)

# print(matches)
# for match in matches:
#     val1 = match[0]
#     op = match[1]
#     val2 = match[2]
#     val3 = match[3]
    
#     if val3 is None:
#         input_string = re.sub(rf"\d+\.{val1}\s*{op}\s*{val2}", f"row['{val1}'] {op} {val2}", input_string)
#     elif val1 == val3:
#         input_string = re.sub(rf"\d+\.{val1}\s*{op}\s*{val3}", f"mfstruct[groupingattributekey]['{val1}'] {op} row['{val3}']",input_string)
#     else:
#         input_string = re.sub(rf"\d+\.{val1}\s*{op}\s*{val3}", f"row['{val1}'] {op} {val3}", input_string)
    



# print(input_string)
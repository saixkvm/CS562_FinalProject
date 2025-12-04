import re

# text = """
# if user.state == "NY":
#     pass
# elif customer.state_code == 'NY':
#     pass
# elif item.statement == "NY":
#     pass
# """

# # The Regex Pattern
# # 1. ([\w.]+)    -> Matches <value> (letters, numbers, underscores, dots)
# # 2. \.state     -> Matches literal ".state"
# # 3. (\w*)       -> Matches <whatever> (optional suffix like _code)
# # 4. \s*==\s* -> Matches "==" with any amount of spaces around it
# # 5. ['"]NY['"]  -> Matches "NY" or 'NY'
# pattern = r"([\w.]+)\.state(\w*)\s*==\s*['\"]NY['\"]"

# matches = re.findall(pattern, text)

# print(f"Found {len(matches)} matches:")
# for match in matches:
#     print(f"Full object: {match[0]}.state{match[1]}")

pattern = r"\w+\.state"
text = "1.state='NY'"
cleaned_expression = re.sub(pattern, 'row["state"]', text)

print(cleaned_expression)
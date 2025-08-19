import json

# create a sample json
a = {"name" : ["GeeksforGeeks", "jest"], "Topic" : "Json to String", "Method": 1}

y = json.dumps(a)

print(y)
print(type(y))
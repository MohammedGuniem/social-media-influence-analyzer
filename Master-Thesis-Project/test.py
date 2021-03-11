import json
d = []
d.append({"a": 1})
d.append({"a": 1})
d.append({"b": 1})
d.append({"a": 2})
d = json.dumps(d)
print(set(d))

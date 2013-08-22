from collections import defaultdict

mydicts = [
   {1:{"Title":"Chrome","Author":"Google","URL":"http://"}},
   {1:{"Title":"Chrome","Author":"Google","Version":"7.0.577.0"}},
   {2:{"Title":"Python","Version":"2.5"}},
]

result = defaultdict(dict)

r2=defaultdict(dict)

for d in mydicts:
    for k, v in d.iteritems():
        result[k].update(v)

from pprint import pprint
pprint( result)

for m in mydicts:
    r2.update(m)

pprint( r2)
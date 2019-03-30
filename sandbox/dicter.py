import sys

def dict_fmt(d):
    s = 'dict({})'
    items = ['{}={}, '.format(key, value) for key, value in d.items()]
    body = ''.join(items)[:-2]
    return s.format(body)

with open(sys.argv[1]) as f:
    txt = f.read()
lines = [line.split() for line in txt.split('\n')][:-1]

headers, body = lines[0], lines[1:]
body = [list(map(int, l)) for l in body]
d = [{header : digit for header, digit in zip(headers, line)} for line in body]

for e in d:
    print(dict_fmt(e)+',')



flags = 'lo lb eu su ea la ei li ce lm ep cp'.split()

passive_state = dict(lo=1, lb=1, eu=1, su=0, ea=1, la=1, ei=1, li=1, ce=0, lm=1, ep=1, cp=0)

def invert_flags(flags):
    d = dict(passive_state)
    for f in flags:
        d[f] = 0 if d[f] else 1
    return d

def gen_mis(instruction):
    ds = [invert_flags(s.split()) for s in instruction]
    mis = []
    for d in ds:
        mi = ''.join([str(d[f]) for f in flags])
        mis.append(mi)
    return mis

f = ['ep lm',
      'cp',
      'ce li']

lda = ['ei lm',
        'ce la',
        '']

add = ['ei lm',
        'ce lb',
        'eu la']

sub = ['ei lm',
       'ce lb su',
       'eu la su']

out = ['ea lo',
        '',
        '']

print(gen_mis(f))
print(gen_mis(lda))
print(gen_mis(add))
print(gen_mis(sub))
print(gen_mis(out))


fa = FullAdder()


fa.watcher = Watcher('stdout')

a = SigGen()
b = SigGen()

fa.connect({'a':a.bus, 'b':b.bus})

for a_sig in a.tt():
    for b_sig in b.tt():
        fa.compute()
        

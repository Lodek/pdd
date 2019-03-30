import sys

n = int(sys.argv[1])
outputs = int(sys.argv[2])

for i in range(2**n):
    line = '{{:0{}b}}'.format(n) + '0'*outputs
    print(' '.join(c for c in line.format(i)))

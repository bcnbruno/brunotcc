import itertools as it 

L = ['a', 'b', 'c', 'd', 'e']
for p in range(2, len(L)+1):
    for c in it.combinations(L, p):
        print(c)

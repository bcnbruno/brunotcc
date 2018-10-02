import random

s = 15
n = 3

sol = []
for i in range(s):
    sol.append(random.randint(0,1))

indexes = list(range(len(sol)))
    
flip_indexes = random.choices(indexes, k=n)

print(' Solução antes:', sol)
for i in flip_indexes:
    sol[i] = int(not bool(sol[i]))

print('Solução depois:', sol)

